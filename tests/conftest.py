import base64
import sqlite3

import pytest

from lib.application import summarizer

from tests.fakes.fake_llm_provider import FakeLLMProvider
from tests.fakes.fake_email_client import FakeEmailClient


def make_message(
    *,
    msg_id: str,
    subject: str = "(No Subject)",
    sender: str = "Unknown",
    snippet: str = "",
    body: str = "",
) -> dict:
    data = base64.urlsafe_b64encode(body.encode("utf-8")).decode("utf-8")
    return {
        "id": msg_id,
        "snippet": snippet,
        "payload": {
            "headers": [
                {"name": "Subject", "value": subject},
                {"name": "From", "value": sender},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": data},
                }
            ],
        },
    }


@pytest.fixture(autouse=True)
def reset_summarizer_state():
    summarizer._reset()
    summarizer.set_llm_provider(FakeLLMProvider())


@pytest.fixture()
def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE emails(
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
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def fake_email_client():
    client = FakeEmailClient()
    return client
