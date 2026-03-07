from lib.adapters.presentation.digest import generate_digest


def test_generate_digest_no_items_shows_empty_message():
    html = generate_digest([], thread_base="#")

    assert "No new emails to show today." in html


def test_generate_digest_groups_and_sorts_by_priority_and_category():
    items = [
        {
            "gmail_id": "1",
            "type": "promo",
            "sender": "Promo Sender",
            "title": "Promo Title",
            "summary": "Promo summary",
            "priority": 1,
        },
        {
            "gmail_id": "2",
            "type": "work",
            "sender": "Boss",
            "title": "Important Work",
            "summary": "Work summary high priority",
            "priority": 5,
        },
        {
            "gmail_id": "3",
            "type": "work",
            "sender": "Colleague",
            "title": "Less Important Work",
            "summary": "Work summary low priority",
            "priority": 2,
        },
    ]

    html = generate_digest(items, thread_base="https://mail.google.com/mail/u/0/#inbox/")

    # Category headers appear
    assert "Work" in html
    assert "Promo" in html

    # Links are composed correctly
    assert 'href="https://mail.google.com/mail/u/0/#inbox/2"' in html

    # Within the Work section, higher priority item should appear first
    assert html.index("Important Work") < html.index("Less Important Work")


def test_generate_digest_includes_cleanup_section_for_stale_items():
    stale_items = [
        {
            "gmail_id": "10",
            "sender": "Old Newsletter",
            "subject": "Old subject",
            "category": "newsletter",
            "priority": 2,
            "processed_at": "2025-01-01 10:00:00",
            "action": "delete",
            "suggested_category": None,
        }
    ]

    html = generate_digest([], stale_items=stale_items, thread_base="https://mail/")

    assert "Tidy up older mail (30+ days)" in html
    assert "Old subject" in html
    assert 'href="https://mail/10"' in html


def test_generate_digest_includes_high_volume_senders():
    high_volume_senders = [
        {
            "sender": "newsletter@example.com",
            "total": 25,
            "categories": {"newsletter": 25},
            "is_newsletter": True,
        },
        {
            "sender": "promo@shop.com",
            "total": 15,
            "categories": {"promo": 15},
            "is_newsletter": False,
        },
    ]

    html = generate_digest([], high_volume_senders=high_volume_senders, thread_base="#")

    assert "High Volume Senders" in html
    assert "newsletter@example.com" in html
    assert "25 emails" in html
    assert "promo@shop.com" in html
    assert "15 emails" in html
    assert "🚨" in html  # Newsletter with 20+ emails
    assert "⚠️" in html  # Other high volume

