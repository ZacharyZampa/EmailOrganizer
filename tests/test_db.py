from pathlib import Path

from lib.adapters.storage import db


def test_get_db_creates_directory_and_schema(tmp_path, monkeypatch):
    test_db_path = tmp_path / "state.db"

    # Point the db module at our temporary location
    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))

    conn = db.get_db()
    try:
        # Database file should exist on disk
        assert Path(test_db_path).exists()

        # emails table should have the expected columns, including account_email
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
    finally:
        conn.close()

