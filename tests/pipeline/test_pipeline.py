from lib.application.run import main
from lib.adapters.storage import db as db_adapter

from tests.fakes.fake_email_client import FakeEmailClient
from tests.conftest import make_message


def test_pipeline_end_to_end(memory_db):
    client = FakeEmailClient(account_email="user@test.com")

    client.messages = {
        "1": make_message(
            msg_id="1",
            subject="Important Work",
            sender="boss@company.com",
            snippet="Please review the document",
            body="Body text",
        ),
        "2": make_message(
            msg_id="2",
            subject="Tech Weekly",
            sender="newsletter@example.com",
            snippet="This week in AI",
            body="Lots of content",
        ),
    }

    client.recent_message_ids = ["1", "2"]
    client.stale_message_ids = ["2"]

    main(email_client=client, db=memory_db)

    assert client.sent_emails
    to, subject, html = client.sent_emails[0]
    assert subject == "Daily Email Digest"
    assert "Daily Email Digest" in html

    assert "1" in client.labels_applied
    assert "2" in client.labels_applied

    row = memory_db.execute("SELECT COUNT(*) FROM emails WHERE account_email=?", ("user@test.com",)).fetchone()
    assert row[0] == 2


def test_pipeline_skips_already_processed(memory_db):
    client = FakeEmailClient(account_email="user@test.com")
    client.messages = {
        "1": make_message(
            msg_id="1",
            subject="Already Done",
            sender="boss@company.com",
            snippet="Please review",
            body="Body",
        )
    }
    client.recent_message_ids = ["1"]

    memory_db.execute(
        "INSERT INTO emails (gmail_id, sender, subject, category, priority, account_email) VALUES (?, ?, ?, ?, ?, ?)",
        ("1", "boss@company.com", "Already Done", "work", 3, "user@test.com"),
    )
    memory_db.commit()

    main(email_client=client, db=memory_db)

    assert client.sent_emails
    row = memory_db.execute("SELECT COUNT(*) FROM emails WHERE account_email=?", ("user@test.com",)).fetchone()
    assert row[0] == 1
