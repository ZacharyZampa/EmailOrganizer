from lib.application.run import get_high_volume_senders, get_recent_sender_aggregation, save_email_to_db


def test_save_email_to_db_round_trip(memory_db):
    save_email_to_db(
        memory_db,
        gmail_id="1",
        sender="a@b.com",
        subject="Subj",
        category="work",
        priority=3,
        account_email="user@test.com",
    )
    memory_db.commit()

    row = memory_db.execute(
        "SELECT sender, subject, category, priority FROM emails WHERE gmail_id=?",
        ("1",),
    ).fetchone()

    assert row == ("a@b.com", "Subj", "work", 3)


def test_get_recent_sender_aggregation_groups(memory_db):
    for i in range(3):
        memory_db.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i}", "news@example.com", f"S{i}", "newsletter", 2, "user@test.com"),
        )
    memory_db.commit()

    result = get_recent_sender_aggregation(memory_db, "user@test.com", days=3, min_count=3)

    assert len(result) == 1
    assert result[0]["sender"] == "news@example.com"
    assert result[0]["count"] == 3


def test_get_high_volume_senders_respects_threshold(memory_db):
    for i in range(5):
        memory_db.execute(
            "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
            (f"id{i}", "low@volume.com", f"Subject {i}", "personal", 3, "user@test.com"),
        )
    memory_db.commit()

    result = get_high_volume_senders(memory_db, "user@test.com", threshold=10)

    assert result == []
