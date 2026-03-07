"""
Default HTML renderer for email digests.
"""

from lib.domain.digest_renderer import DigestRenderer
from lib.domain.digest_data import DigestData

CATEGORY_BADGE = {
    "work": ("💼", "#e8f0fe", "#1a73e8"),
    "finance": ("💰", "#fce8e6", "#d93025"),
    "newsletter": ("📰", "#e6f4ea", "#188038"),
    "personal": ("👤", "#f3e8fd", "#7b1fa2"),
    "promo": ("🏷️", "#fef3e2", "#e37400"),
    "spam": ("🚫", "#f1f3f4", "#999999"),
}

CATEGORY_ORDER = ["work", "finance", "personal", "newsletter", "promo", "spam", "other"]


def _extract_unsubscribe_link(email_body: str) -> str | None:
    """Extract unsubscribe link from email body."""
    import re
    # Look for common unsubscribe patterns
    patterns = [
        r'https?://[^\s<>"]+unsubscribe[^\s<>"]*',
        r'https?://[^\s<>"]+/optout[^\s<>"]*',
        r'https?://[^\s<>"]+/remove[^\s<>"]*',
    ]
    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


class DefaultHTMLRenderer(DigestRenderer):
    """Default HTML email digest renderer."""

    def render(self, data: DigestData) -> str:
        """Render digest data as HTML."""
        digest_sections = self._render_digest_sections(data.emails, data.thread_base)
        recent_agg_section = self._render_recent_aggregation_section(
            getattr(data, 'recent_aggregation', []), 
            data.thread_base
        )
        volume_section = self._render_high_volume_section(data.high_volume_senders)
        cleanup_section = self._render_cleanup_section(data.stale_emails, data.thread_base)

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f7fb;
    margin: 0;
    padding: 20px;
    color: #1a1a1a;
}}
.container {{ max-width: 720px; margin: auto; }}
.title {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
.subtitle {{ color: #666; margin-bottom: 20px; }}
.card {{
    display: block;
    text-decoration: none;
    color: inherit;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}}
.card:hover {{ box-shadow: 0 4px 14px rgba(0,0,0,0.1); }}
.card-meta {{
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 6px;
    font-size: 12px;
    color: #666;
}}
.badge {{ font-weight: 600; }}
.sender {{ flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.priority {{ font-weight: 600; }}
.card-title {{ font-weight: 600; font-size: 15px; margin-bottom: 6px; }}
.card-summary {{ color: #444; line-height: 1.5; font-size: 14px; }}
.category-block + .category-block {{ margin-top: 16px; }}
.category-header {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #555;
    margin: 18px 0 6px;
}}
.section-heading {{
    margin-top: 28px;
    font-size: 16px;
    font-weight: 650;
}}
.section-subtitle {{
    margin-top: 4px;
    margin-bottom: 12px;
    color: #666;
    font-size: 13px;
}}
.cleanup-list {{
    margin-top: 4px;
}}
.cleanup-card {{
    display: block;
    text-decoration: none;
    color: inherit;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    background: #f1f3f4;
}}
.cleanup-meta {{
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #777;
    margin-bottom: 3px;
}}
.cleanup-title {{
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 2px;
}}
.cleanup-sender {{
    font-size: 12px;
    color: #666;
}}
.volume-list {{
    margin-top: 8px;
}}
.volume-card {{
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    background: #fff3e0;
    border-left: 3px solid #ff9800;
}}
.volume-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}}
.volume-flag {{
    font-size: 16px;
}}
.volume-sender {{
    flex: 1;
    font-weight: 600;
    font-size: 14px;
}}
.volume-count {{
    font-size: 12px;
    font-weight: 600;
    color: #e65100;
}}
.volume-breakdown {{
    font-size: 12px;
    color: #666;
}}
.recent-agg-list {{ margin-top: 8px; }}
.recent-agg-card {{ border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; background: #e3f2fd; border-left: 3px solid #2196f3; }}
.agg-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
.agg-emoji {{ font-size: 18px; }}
.agg-sender {{ flex: 1; font-weight: 600; font-size: 14px; }}
.agg-info {{ display: flex; justify-content: space-between; font-size: 12px; color: #555; margin-bottom: 8px; }}
.agg-count {{ font-weight: 500; }}
.agg-category {{ text-transform: capitalize; color: #666; }}
.agg-actions {{ display: flex; gap: 8px; }}
.action-btn {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; text-decoration: none; transition: all 0.2s; }}
.delete-btn {{ background: #ffebee; color: #c62828; border: 1px solid #ef5350; }}
.delete-btn:hover {{ background: #ef5350; color: white; }}
.unsub-btn {{ background: #fff3e0; color: #e65100; border: 1px solid #ff9800; }}
.unsub-btn:hover {{ background: #ff9800; color: white; }}
.footer {{ margin-top: 24px; font-size: 13px; color: #888; }}
</style>
</head>
<body>
<div class="container">
    <div class="title">📬 Daily Email Digest</div>
    <div class="subtitle">AI summary of today's emails</div>
    {digest_sections}
    {recent_agg_section}
    {volume_section}
    {cleanup_section}
    <div class="footer">Generated locally · {len(data.emails)} email(s) summarised</div>
</div>
</body>
</html>
"""
        return html

    def _render_digest_sections(self, emails, thread_base: str):
        """Render main email digest sections."""
        if not emails:
            return "<p style='color:#888'>No new emails to show today.</p>"

        grouped = {}
        for email in emails:
            ctype = email.type
            grouped.setdefault(ctype, []).append(email)

        for group_items in grouped.values():
            group_items.sort(key=lambda x: -x.priority)

        def _category_sort_key(cat):
            try:
                return CATEGORY_ORDER.index(cat)
            except ValueError:
                return len(CATEGORY_ORDER)

        sections = ""
        for category in sorted(grouped.keys(), key=_category_sort_key):
            group_items = grouped[category]
            if not group_items:
                continue

            emoji, _, color = CATEGORY_BADGE.get(category, ("📧", "#f5f5f5", "#333"))
            sections += f"""
    <div class="category-block">
        <div class="category-header">{emoji} {category.title()}</div>
    """
            for email in group_items:
                _, bg, card_color = CATEGORY_BADGE.get(email.type, ("📧", "#f5f5f5", "#333"))
                link = f"{thread_base}{email.gmail_id}"
                sections += f"""
        <a href="{link}" class="card" style="border-left: 4px solid {card_color}; background: {bg}">
            <div class="card-meta">
                <span class="sender">{email.sender}</span>
                <span class="priority">P{email.priority}</span>
            </div>
            <div class="card-title">{email.title}</div>
            <div class="card-summary">{email.summary}</div>
        </a>
    """
            sections += "</div>"

        return sections

    def _render_high_volume_section(self, high_volume_senders):
        """Render high volume senders section."""
        if not high_volume_senders:
            return ""

        cards = ""
        for sender_info in high_volume_senders:
            sender = sender_info.sender
            total = sender_info.total
            categories = sender_info.categories
            is_newsletter = sender_info.is_newsletter
            
            cat_breakdown = ", ".join([f"{cat}: {count}" for cat, count in categories.items()])
            flag = "🚨" if is_newsletter and total > 20 else "⚠️"
            
            cards += f"""
        <div class="volume-card">
            <div class="volume-header">
                <span class="volume-flag">{flag}</span>
                <span class="volume-sender">{sender}</span>
                <span class="volume-count">{total} emails</span>
            </div>
            <div class="volume-breakdown">{cat_breakdown}</div>
        </div>
    """

        return f"""
    <div class="section-heading">📊 High Volume Senders (All Time)</div>
    <p class="section-subtitle">Senders with 10+ emails total. Consider unsubscribing from newsletters.</p>
    <div class="volume-list">
        {cards}
    </div>
    """

    def _render_recent_aggregation_section(self, recent_aggregation, thread_base: str):
        """Render recent sender aggregation with action links."""
        if not recent_aggregation:
            return ""

        cards = ""
        for agg in recent_aggregation:
            sender = agg["sender"]
            count = agg["count"]
            category = agg["category"]
            gmail_ids = agg["gmail_ids"]
            is_newsletter = agg["is_newsletter"]
            
            # Create delete all link (Gmail search)
            delete_search = f"from:{sender}"
            delete_link = f"https://mail.google.com/mail/u/0/#search/{delete_search}"
            
            # Get first email for potential unsubscribe link
            first_email_link = f"{thread_base}{gmail_ids[0]}" if gmail_ids else "#"
            
            action_buttons = f'<a href="{delete_link}" class="action-btn delete-btn">Delete All</a>'
            if is_newsletter:
                action_buttons += f' <a href="{first_email_link}" class="action-btn unsub-btn">View to Unsubscribe</a>'
            
            emoji = "📰" if is_newsletter else "📧"
            
            cards += f"""
        <div class="recent-agg-card">
            <div class="agg-header">
                <span class="agg-emoji">{emoji}</span>
                <span class="agg-sender">{sender}</span>
            </div>
            <div class="agg-info">
                <span class="agg-count">{count} emails in past 3 days</span>
                <span class="agg-category">{category}</span>
            </div>
            <div class="agg-actions">
                {action_buttons}
            </div>
        </div>
    """

        return f"""
    <div class="section-heading">📬 Recent Email Patterns</div>
    <p class="section-subtitle">Senders who emailed you 3+ times in the past 3 days.</p>
    <div class="recent-agg-list">
        {cards}
    </div>
    """

    def _render_cleanup_section(self, stale_emails, thread_base: str):
        """Render stale email cleanup section."""
        if not stale_emails:
            return ""

        cards = ""
        for email in stale_emails:
            date_str = (email.processed_at or "").split(" ")[0]
            action = email.action
            suggested_category = email.suggested_category
            action_text = action.capitalize()
            if suggested_category:
                action_text += f" → {suggested_category}"

            link = f"{thread_base}{email.gmail_id}"
            cards += f"""
        <a href="{link}" class="cleanup-card">
            <div class="cleanup-meta">
                <span class="cleanup-date">{date_str}</span>
                <span class="cleanup-action">{action_text}</span>
            </div>
            <div class="cleanup-title">{email.subject}</div>
            <div class="cleanup-sender">{email.sender}</div>
        </a>
    """

        return f"""
    <div class="section-heading">🧹 Tidy up older mail (30+ days)</div>
    <p class="section-subtitle">Quick suggestions for messages that have been sitting for a while.</p>
    <div class="cleanup-list">
        {cards}
    </div>
    """


def _render_digest_sections(items, thread_base: str):
    if not items:
        return "<p style='color:#888'>No new emails to show today.</p>"

    # Group by category and sort items by priority (highest first)
    grouped = {}
    for item in items:
        ctype = item.get("type", "other")
        grouped.setdefault(ctype, []).append(item)

    for ctype, group_items in grouped.items():
        group_items.sort(key=lambda x: -x.get("priority", 0))

    def _category_sort_key(cat):
        try:
            return CATEGORY_ORDER.index(cat)
        except ValueError:
            return len(CATEGORY_ORDER)

    sections = ""
    for category in sorted(grouped.keys(), key=_category_sort_key):
        group_items = grouped[category]
        if not group_items:
            continue

        emoji, _, color = CATEGORY_BADGE.get(category, ("📧", "#f5f5f5", "#333"))
        sections += f"""
    <div class="category-block">
        <div class="category-header">{emoji} {category.title()}</div>
    """
        for item in group_items:
            _, bg, card_color = CATEGORY_BADGE.get(
                item["type"], ("📧", "#f5f5f5", "#333")
            )
            link = f"{thread_base}{item['gmail_id']}"
            sections += f"""
        <a href="{link}" class="card" style="border-left: 4px solid {card_color}; background: {bg}">
            <div class="card-meta">
                <span class="sender">{item['sender']}</span>
                <span class="priority">P{item['priority']}</span>
            </div>
            <div class="card-title">{item['title']}</div>
            <div class="card-summary">{item['summary']}</div>
        </a>
    """
        sections += "</div>"

    return sections


def _render_cleanup_section(stale_items, thread_base: str):
    if not stale_items:
        return ""

    cards = ""
    for item in stale_items:
        date_str = (item.get("processed_at") or "").split(" ")[0]
        action = item.get("action", "review")
        suggested_category = item.get("suggested_category")
        action_text = action.capitalize()
        if suggested_category:
            action_text += f" → {suggested_category}"

        link = f"{thread_base}{item['gmail_id']}"
        cards += f"""
        <a href="{link}" class="cleanup-card">
            <div class="cleanup-meta">
                <span class="cleanup-date">{date_str}</span>
                <span class="cleanup-action">{action_text}</span>
            </div>
            <div class="cleanup-title">{item['subject']}</div>
            <div class="cleanup-sender">{item['sender']}</div>
        </a>
    """

    return f"""
    <div class="section-heading">🧹 Tidy up older mail (30+ days)</div>
    <p class="section-subtitle">Quick suggestions for messages that have been sitting for a while.</p>
    <div class="cleanup-list">
        {cards}
    </div>
    """


def _render_high_volume_section(high_volume_senders):
    if not high_volume_senders:
        return ""

    cards = ""
    for sender_info in high_volume_senders:
        sender = sender_info["sender"]
        total = sender_info["total"]
        categories = sender_info["categories"]
        is_newsletter = sender_info["is_newsletter"]
        
        cat_breakdown = ", ".join([f"{cat}: {count}" for cat, count in categories.items()])
        flag = "🚨" if is_newsletter and total > 20 else "⚠️"
        
        cards += f"""
        <div class="volume-card">
            <div class="volume-header">
                <span class="volume-flag">{flag}</span>
                <span class="volume-sender">{sender}</span>
                <span class="volume-count">{total} emails</span>
            </div>
            <div class="volume-breakdown">{cat_breakdown}</div>
        </div>
    """

    return f"""
    <div class="section-heading">📊 High Volume Senders</div>
    <p class="section-subtitle">Senders with 10+ emails. Consider unsubscribing from newsletters.</p>
    <div class="volume-list">
        {cards}
    </div>
    """


def generate_digest(items, stale_items=None, high_volume_senders=None, thread_base: str = "#"):
    digest_sections = _render_digest_sections(items, thread_base)
    cleanup_section = _render_cleanup_section(stale_items or [], thread_base)
    volume_section = _render_high_volume_section(high_volume_senders or [])

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f7fb;
    margin: 0;
    padding: 20px;
    color: #1a1a1a;
}}
.container {{ max-width: 720px; margin: auto; }}
.title {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
.subtitle {{ color: #666; margin-bottom: 20px; }}
.card {{
    display: block;
    text-decoration: none;
    color: inherit;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}}
.card:hover {{ box-shadow: 0 4px 14px rgba(0,0,0,0.1); }}
.card-meta {{
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 6px;
    font-size: 12px;
    color: #666;
}}
.badge {{ font-weight: 600; }}
.sender {{ flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.priority {{ font-weight: 600; }}
.card-title {{ font-weight: 600; font-size: 15px; margin-bottom: 6px; }}
.card-summary {{ color: #444; line-height: 1.5; font-size: 14px; }}
.category-block + .category-block {{ margin-top: 16px; }}
.category-header {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #555;
    margin: 18px 0 6px;
}}
.section-heading {{
    margin-top: 28px;
    font-size: 16px;
    font-weight: 650;
}}
.section-subtitle {{
    margin-top: 4px;
    margin-bottom: 12px;
    color: #666;
    font-size: 13px;
}}
.cleanup-list {{
    margin-top: 4px;
}}
.cleanup-card {{
    display: block;
    text-decoration: none;
    color: inherit;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    background: #f1f3f4;
}}
.cleanup-meta {{
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #777;
    margin-bottom: 3px;
}}
.cleanup-title {{
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 2px;
}}
.cleanup-sender {{
    font-size: 12px;
    color: #666;
}}
.volume-list {{
    margin-top: 8px;
}}
.volume-card {{
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    background: #fff3e0;
    border-left: 3px solid #ff9800;
}}
.volume-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}}
.volume-flag {{
    font-size: 16px;
}}
.volume-sender {{
    flex: 1;
    font-weight: 600;
    font-size: 14px;
}}
.volume-count {{
    font-size: 12px;
    font-weight: 600;
    color: #e65100;
}}
.volume-breakdown {{
    font-size: 12px;
    color: #666;
}}
.footer {{ margin-top: 24px; font-size: 13px; color: #888; }}
</style>
</head>
<body>
<div class="container">
    <div class="title">📬 Daily Email Digest</div>
    <div class="subtitle">AI summary of today's emails</div>
    {digest_sections}
    {volume_section}
    {cleanup_section}
    <div class="footer">Generated locally · {len(items)} email(s) summarised</div>
</div>
</body>
</html>
"""
    return html


# Backward compatibility function
def generate_digest(items, stale_items=None, high_volume_senders=None, recent_aggregation=None, thread_base: str = "#"):
    """
    Generate HTML digest (backward compatibility wrapper).
    
    For new code, use DigestData + DigestRenderer directly.
    """
    from lib.domain.digest_data import DigestData, DigestEmail, StaleEmail, HighVolumeSender
    
    emails = [DigestEmail(**item) for item in items]
    stale = [StaleEmail(**item) for item in (stale_items or [])]
    volume = [HighVolumeSender(**item) for item in (high_volume_senders or [])]
    
    data = DigestData(
        emails=emails,
        stale_emails=stale,
        high_volume_senders=volume,
        thread_base=thread_base
    )
    
    # Add recent_aggregation as dynamic attribute
    data.recent_aggregation = recent_aggregation or []
    
    renderer = DefaultHTMLRenderer()
    return renderer.render(data)
