import os
import sqlite3

from lib.config import DB_PATH


def get_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS emails(
            gmail_id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            category TEXT,
            priority INTEGER,
            newsletter INTEGER,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            account_email TEXT
        )
        """
    )
    # Ensure multi-account support for older databases that predate account_email.
    cur = conn.execute("PRAGMA table_info(emails)")
    cols = {row[1] for row in cur.fetchall()}
    if "account_email" not in cols:
        conn.execute("ALTER TABLE emails ADD COLUMN account_email TEXT")
    return conn
