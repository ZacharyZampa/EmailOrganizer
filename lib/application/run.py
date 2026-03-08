
from typing import Any, Optional
import base64

from lib.adapters.storage.db import get_db
from lib.adapters.email.gmail_client import GmailClient
from lib.application.summarizer import categorize_email, summarize_with_plugins
from lib.adapters.presentation.digest import generate_digest
from lib.config import (
    EMAIL_ADDRESSES,
    EMAIL_THREAD_BASES,
    INTERESTS,
    PRIORITY_THRESHOLD,
    GMAIL_DIGEST_LABEL,
    GMAIL_CATEGORY_LABEL_PREFIX,
    HIGH_VOLUME_SENDER_THRESHOLD,
    STALE_EMAIL_MAX_RESULTS,
)


def get_body(msg: dict[str, Any]) -> str:
    """Extract plain text body from a Gmail message."""
    payload = msg.get("payload", {})

    if "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")

    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return msg.get("snippet", "")


def get_header(headers: list[dict[str, str]], name: str, default: str = "") -> str:
    """Extract a header value by name."""
    return next((h["value"] for h in headers if h["name"] == name), default)


def save_email_to_db(
    db: Any, 
    gmail_id: str, 
    sender: str, 
    subject: str, 
    category: str, 
    priority: int, 
    account_email: str
) -> None:
    """Insert email record into database."""
    db.execute(
        """
        INSERT INTO emails (
            gmail_id, sender, subject, category, priority, account_email
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (gmail_id, sender, subject, category, priority, account_email),
    )


def process_message_metadata(msg: dict[str, Any]) -> tuple[str, str, str]:
    """Extract subject, sender, and snippet from a message."""
    headers = msg["payload"]["headers"]
    subject = get_header(headers, "Subject", "(No Subject)")
    sender = get_header(headers, "From", "Unknown")
    snippet = msg.get("snippet", "")
    return subject, sender, snippet


def get_high_volume_senders(
    db: Any, 
    account_email: str, 
    threshold: int = HIGH_VOLUME_SENDER_THRESHOLD
) -> list[dict[str, Any]]:
    """
    Find senders with high email volume, especially newsletters that aren't deleted.
    Returns list of dicts with sender, count, and category breakdown.
    """
    rows = db.execute(
        """
        SELECT sender, category, COUNT(*) as count
        FROM emails
        WHERE account_email = ?
        GROUP BY sender, category
        HAVING count >= ?
        ORDER BY count DESC
        """,
        (account_email, threshold),
    ).fetchall()
    
    sender_stats = {}
    for sender, category, count in rows:
        if sender not in sender_stats:
            sender_stats[sender] = {"sender": sender, "total": 0, "categories": {}}
        sender_stats[sender]["total"] += count
        sender_stats[sender]["categories"][category] = count
    
    return [
        {
            "sender": stats["sender"],
            "total": stats["total"],
            "categories": stats["categories"],
            "is_newsletter": "newsletter" in stats["categories"],
        }
        for stats in sender_stats.values()
    ]


def get_recent_sender_aggregation(
    db: Any,
    account_email: str,
    days: int = 3,
    min_count: int = 3
) -> list[dict[str, Any]]:
    """
    Aggregate recent emails by sender to show patterns.
    
    Returns senders who sent multiple emails in the past N days.
    """
    rows = db.execute(
        """
        SELECT sender, category, COUNT(*) as count,
               GROUP_CONCAT(gmail_id) as gmail_ids
        FROM emails
        WHERE account_email = ?
          AND datetime(processed_at) >= datetime('now', '-' || ? || ' days')
        GROUP BY sender, category
        HAVING count >= ?
        ORDER BY count DESC
        """,
        (account_email, days, min_count),
    ).fetchall()
    
    result = []
    for sender, category, count, gmail_ids in rows:
        result.append({
            "sender": sender,
            "category": category,
            "count": count,
            "gmail_ids": gmail_ids.split(",") if gmail_ids else [],
            "is_newsletter": category == "newsletter",
        })
    
    return result


def _process_and_categorize_email(
    email_client: Any,
    db: Any,
    gmail_id: str,
    account_email: str
) -> tuple[str, str, str, str, int]:
    """
    Process a single email: fetch, extract metadata, categorize.
    
    Returns: (subject, sender, snippet, category, priority)
    """
    msg = email_client.get_message(gmail_id)
    subject, sender, snippet = process_message_metadata(msg)
    
    result = categorize_email(snippet)
    category = result["category"]
    priority = result["priority"]
    
    save_email_to_db(db, gmail_id, sender, subject, category, priority, account_email)
    
    return subject, sender, snippet, category, priority


def main(email_client: Optional[Any] = None, db: Optional[Any] = None) -> None:
    """
    Main email processing pipeline.
    
    Args:
        email_client: Optional EmailClient implementation. Defaults to GmailClient.
        db: Optional database connection. Defaults to get_db().
    """
    if email_client is None:
        email_client = GmailClient()
    
    if db is None:
        db = get_db()
    account_email = email_client.get_account_email()

    msgs = email_client.get_recent_messages()
    digest_items = []

    for m in msgs:
        gmail_id = m["id"]

        if db.execute(
            "SELECT gmail_id FROM emails WHERE gmail_id=? AND account_email=?",
            (gmail_id, account_email),
        ).fetchone():
            continue

        msg = email_client.get_message(gmail_id)
        subject, sender, snippet = process_message_metadata(msg)
        body = get_body(msg)

        result = categorize_email(snippet)
        category = result["category"]
        priority = result["priority"]

        label_names = [
            GMAIL_DIGEST_LABEL,
            f"{GMAIL_CATEGORY_LABEL_PREFIX}{category.capitalize()}",
        ]
        email_client.add_labels(gmail_id, label_names)

        # Use plugin system for summarization
        if category in ("work", "finance", "newsletter") or priority >= PRIORITY_THRESHOLD:
            email_data = {
                "subject": subject,
                "sender": sender,
                "body": body,
                "snippet": snippet,
            }
            context = {
                "interests": INTERESTS,
                "priority_threshold": PRIORITY_THRESHOLD,
            }
            
            summary = summarize_with_plugins(category, email_data, context)
            
            digest_items.append({
                "gmail_id": gmail_id,
                "type": category,
                "title": subject,
                "sender": sender,
                "summary": summary,
                "priority": priority,
            })

        save_email_to_db(db, gmail_id, sender, subject, category, priority, account_email)

    db.commit()

    stale_items = []
    stale_msgs = email_client.get_stale_messages(max_results=STALE_EMAIL_MAX_RESULTS)

    for m in stale_msgs:
        gmail_id = m["id"]
        row = db.execute(
            """
            SELECT sender, subject, category, priority, processed_at
            FROM emails
            WHERE gmail_id=? AND account_email=?
            """,
            (gmail_id, account_email),
        ).fetchone()

        if not row:
            subject, sender, snippet, category, priority = _process_and_categorize_email(
                email_client, db, gmail_id, account_email
            )
            db.commit()
            row = (sender, subject, category, priority, None)

        sender, subject, category, priority, processed_at = row

        if category in ("spam", "promo") or (category == "newsletter" and priority <= 3):
            action = "delete"
            suggested_category = None
        else:
            action = "move"
            suggested_category = category.title()

        stale_items.append({
            "gmail_id": gmail_id,
            "sender": sender,
            "subject": subject,
            "category": category,
            "priority": priority,
            "processed_at": processed_at,
            "action": action,
            "suggested_category": suggested_category,
        })

    high_volume_senders = get_high_volume_senders(db, account_email)
    recent_aggregation = get_recent_sender_aggregation(db, account_email)

    for addr in EMAIL_ADDRESSES:
        thread_base = EMAIL_THREAD_BASES.get(addr) or next(iter(EMAIL_THREAD_BASES.values()))
        html = generate_digest(
            digest_items, 
            stale_items=stale_items, 
            high_volume_senders=high_volume_senders,
            recent_aggregation=recent_aggregation,
            thread_base=thread_base
        )
        email_client.send_email(addr, "Daily Email Digest", html)


if __name__ == "__main__":
    main()
