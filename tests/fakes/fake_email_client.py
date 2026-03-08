from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from lib.domain.email_client import EmailClient


@dataclass
class FakeEmailClient(EmailClient):
    messages: dict[str, dict[str, Any]] = field(default_factory=dict)
    recent_message_ids: list[str] = field(default_factory=list)
    stale_message_ids: list[str] = field(default_factory=list)
    account_email: str = "user@test.com"

    labels_applied: dict[str, list[str]] = field(default_factory=dict)
    sent_emails: list[tuple[str, str, str]] = field(default_factory=list)

    def get_recent_messages(self, days: int = 3) -> list[dict[str, Any]]:
        return [{"id": mid} for mid in self.recent_message_ids]

    def get_message(self, msg_id: str) -> dict[str, Any]:
        return self.messages[msg_id]

    def get_stale_messages(self, days: int = 30, max_results: int = 50) -> list[dict[str, Any]]:
        ids = list(self.stale_message_ids)
        if max_results and max_results > 0:
            ids = ids[:max_results]
        return [{"id": mid} for mid in ids]

    def add_labels(self, msg_id: str, labels: list[str]) -> None:
        self.labels_applied[msg_id] = list(labels)

    def send_email(self, to: str, subject: str, html: str) -> None:
        self.sent_emails.append((to, subject, html))

    def get_account_email(self) -> str:
        return self.account_email
