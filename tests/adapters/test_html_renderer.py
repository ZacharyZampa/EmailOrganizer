from lib.adapters.presentation.digest import DefaultHTMLRenderer
from lib.domain.digest_data import DigestData, DigestEmail, HighVolumeSender, StaleEmail


def test_html_renderer_empty(snapshot):
    data = DigestData(
        emails=[],
        stale_emails=[],
        high_volume_senders=[],
        thread_base="https://mail.google.com/mail/u/0/#inbox/",
    )
    data.recent_aggregation = []

    renderer = DefaultHTMLRenderer()
    assert renderer.render(data) == snapshot


def test_html_renderer_full(snapshot):
    data = DigestData(
        emails=[
            DigestEmail(
                gmail_id="2",
                type="work",
                title="Important Work",
                sender="Boss",
                summary="Work summary high priority",
                priority=5,
            ),
            DigestEmail(
                gmail_id="1",
                type="promo",
                title="Promo Title",
                sender="Promo Sender",
                summary="Promo summary",
                priority=1,
            ),
        ],
        stale_emails=[
            StaleEmail(
                gmail_id="10",
                sender="Old Newsletter",
                subject="Old subject",
                category="newsletter",
                priority=2,
                processed_at="2025-01-01 10:00:00",
                action="delete",
                suggested_category=None,
            )
        ],
        high_volume_senders=[
            HighVolumeSender(
                sender="newsletter@example.com",
                total=25,
                categories={"newsletter": 25},
                is_newsletter=True,
            ),
            HighVolumeSender(
                sender="promo@shop.com",
                total=15,
                categories={"promo": 15},
                is_newsletter=False,
            ),
        ],
        thread_base="https://mail.google.com/mail/u/0/#inbox/",
    )

    data.recent_aggregation = [
        {
            "sender": "newsletter@example.com",
            "count": 3,
            "category": "newsletter",
            "gmail_ids": ["2", "3", "4"],
            "is_newsletter": True,
        }
    ]

    renderer = DefaultHTMLRenderer()
    assert renderer.render(data) == snapshot
