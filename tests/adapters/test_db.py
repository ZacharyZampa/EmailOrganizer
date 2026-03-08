from pathlib import Path

from lib.adapters.storage import db


def test_get_db_creates_directory_and_schema(tmp_path, monkeypatch):
    test_db_path = tmp_path / "state.db"

    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))

    conn = db.get_db()
    try:
        assert Path(test_db_path).exists()

        cur = conn.execute("PRAGMA table_info(emails)")
        cols = {row[1] for row in cur.fetchall()}

        for expected in [
            "gmail_id",
            "sender",
            "subject",
            "category",
            "priority",
            "processed_at",
            "account_email",
        ]:
            assert expected in cols

        conn.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            ("1", "a@b.com", "Subj", "work", 3, "user@test.com"),
        )
        conn.commit()

        row = conn.execute("SELECT sender FROM emails WHERE gmail_id=?", ("1",)).fetchone()
        assert row == ("a@b.com",)
    finally:
        conn.close()
