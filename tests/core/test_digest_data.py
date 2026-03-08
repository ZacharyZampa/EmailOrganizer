from lib.domain.digest_data import DigestData, DigestEmail, HighVolumeSender, StaleEmail


def test_digest_data_constructs():
    data = DigestData(
        emails=[
            DigestEmail(
                gmail_id="1",
                type="work",
                title="Subject",
                sender="sender@example.com",
                summary="summary",
                priority=3,
            )
        ],
        stale_emails=[
            StaleEmail(
                gmail_id="2",
                sender="old@example.com",
                subject="Old",
                category="promo",
                priority=1,
                processed_at=None,
                action="delete",
                suggested_category=None,
            )
        ],
        high_volume_senders=[
            HighVolumeSender(sender="news@example.com", total=10, categories={"newsletter": 10}, is_newsletter=True)
        ],
        thread_base="#",
    )

    assert data.emails[0].gmail_id == "1"
    assert data.stale_emails[0].action == "delete"
    assert data.high_volume_senders[0].total == 10
