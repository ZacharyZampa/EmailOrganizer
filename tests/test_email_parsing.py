import base64

from lib.application.run import get_body, get_header, process_message_metadata


def test_get_header_extracts_value():
    headers = [
        {"name": "Subject", "value": "Test Subject"},
        {"name": "From", "value": "test@example.com"},
    ]

    assert get_header(headers, "Subject") == "Test Subject"
    assert get_header(headers, "From") == "test@example.com"
    assert get_header(headers, "To", "default") == "default"


def test_get_body_prefers_text_plain_part():
    data = base64.urlsafe_b64encode(b"Hello").decode("utf-8")
    msg = {
        "snippet": "snippet",
        "payload": {
            "headers": [],
            "parts": [
                {"mimeType": "text/plain", "body": {"data": data}},
            ],
        },
    }

    assert get_body(msg) == "Hello"


def test_process_message_metadata_extracts_fields():
    msg = {
        "snippet": "snip",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Hi"},
                {"name": "From", "value": "a@b.com"},
            ]
        },
    }

    subject, sender, snippet = process_message_metadata(msg)
    assert subject == "Hi"
    assert sender == "a@b.com"
    assert snippet == "snip"
