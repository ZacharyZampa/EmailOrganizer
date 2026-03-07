import sqlite3
from lib.application.run import get_header, get_high_volume_senders


def test_get_header_extracts_value():
    headers = [
        {"name": "Subject", "value": "Test Subject"},
        {"name": "From", "value": "test@example.com"},
    ]
    
    assert get_header(headers, "Subject") == "Test Subject"
    assert get_header(headers, "From") == "test@example.com"
    assert get_header(headers, "To", "default") == "default"


def test_get_high_volume_senders_aggregates_by_sender():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE emails (
            gmail_id TEXT,
            sender TEXT,
            subject TEXT,
            category TEXT,
            priority INTEGER,
            account_email TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    for i in range(15):
        conn.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i}", "newsletter@example.com", f"Subject {i}", "newsletter", 2, "user@test.com")
        )
    
    for i in range(12):
        conn.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i+15}", "promo@shop.com", f"Promo {i}", "promo", 1, "user@test.com")
        )
    
    for i in range(5):
        conn.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i+27}", "work@company.com", f"Work {i}", "work", 4, "user@test.com")
        )
    
    conn.commit()
    
    result = get_high_volume_senders(conn, "user@test.com", threshold=10)
    
    assert len(result) == 2
    assert result[0]["sender"] == "newsletter@example.com"
    assert result[0]["total"] == 15
    assert result[0]["is_newsletter"] is True
    assert result[1]["sender"] == "promo@shop.com"
    assert result[1]["total"] == 12
    assert result[1]["is_newsletter"] is False
    
    conn.close()


def test_get_high_volume_senders_respects_threshold():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE emails (
            gmail_id TEXT,
            sender TEXT,
            subject TEXT,
            category TEXT,
            priority INTEGER,
            account_email TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    for i in range(5):
        conn.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i}", "low@volume.com", f"Subject {i}", "personal", 3, "user@test.com")
        )
    
    conn.commit()
    
    result = get_high_volume_senders(conn, "user@test.com", threshold=10)
    
    assert len(result) == 0
    
    conn.close()
