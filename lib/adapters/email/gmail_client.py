"""
Gmail implementation of the email client interface.
"""

import base64
import os
import time
from email.mime.text import MIMEText
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from lib.domain.email_client import EmailClient
from lib.config import (
    GMAIL_DIGEST_LABEL,
    GMAIL_API_REQUESTS_PER_SECOND,
    GMAIL_API_RETRY_ATTEMPTS,
    GMAIL_API_RETRY_DELAY,
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

_LABEL_CACHE = {}


class GmailClient(EmailClient):
    """Gmail API implementation of EmailClient with rate limiting."""

    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self._service = None
        self._last_request_time = 0.0
        self._min_request_interval = 1.0 / GMAIL_API_REQUESTS_PER_SECOND

    def _rate_limit(self):
        """Enforce rate limiting between API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _retry_request(self, func, *args, **kwargs):
        """Retry API request with exponential backoff."""
        for attempt in range(GMAIL_API_RETRY_ATTEMPTS):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except HttpError as e:
                if e.resp.status in (429, 500, 503) and attempt < GMAIL_API_RETRY_ATTEMPTS - 1:
                    delay = GMAIL_API_RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise
        raise RuntimeError("Max retry attempts exceeded")

    def _get_service(self):
        """Lazily initialize Gmail API service."""
        if self._service:
            return self._service

        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None

            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "w") as f:
                f.write(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def get_recent_messages(self, days: int = 3) -> list[dict[str, Any]]:
        """Fetch recent messages from Gmail."""
        service = self._get_service()
        results = self._retry_request(
            lambda: service.users().messages().list(
                userId="me",
                q=f"newer_than:{days}d"
            ).execute()
        )
        return results.get("messages", [])

    def get_message(self, msg_id: str) -> dict[str, Any]:
        """Fetch full message from Gmail."""
        service = self._get_service()
        return self._retry_request(
            lambda: service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full"
            ).execute()
        )

    def get_stale_messages(self, days: int = 30, max_results: int = 50) -> list[dict[str, Any]]:
        """
        Fetch old messages still in inbox with pagination support.
        
        Args:
            days: Age threshold in days
            max_results: Maximum messages to return (0 = fetch all)
        """
        service = self._get_service()
        query = f'in:inbox older_than:{days}d'
        
        all_messages = []
        page_token = None
        
        # If max_results is 0, fetch everything
        fetch_all = max_results == 0
        
        while True:
            # Fetch up to 500 per page (Gmail API limit)
            page_size = 500 if fetch_all else min(max_results - len(all_messages), 500)
            
            if page_size <= 0:
                break
            
            request_params = {
                "userId": "me",
                "q": query,
                "maxResults": page_size
            }
            
            if page_token:
                request_params["pageToken"] = page_token
            
            results = self._retry_request(
                lambda: service.users().messages().list(**request_params).execute()
            )
            
            messages = results.get("messages", [])
            all_messages.extend(messages)
            
            page_token = results.get("nextPageToken")
            
            # Stop if no more pages or we've hit the limit
            if not page_token or (not fetch_all and len(all_messages) >= max_results):
                break
        
        return all_messages

    def add_labels(self, msg_id: str, labels: list[str]) -> None:
        """Add Gmail labels to a message."""
        if not labels:
            return

        service = self._get_service()
        label_ids = [self._ensure_label(name) for name in labels]
        self._retry_request(
            lambda: service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"addLabelIds": label_ids},
            ).execute()
        )

    def send_email(self, to: str, subject: str, html: str) -> None:
        """Send an email via Gmail."""
        service = self._get_service()
        msg = MIMEText(html, "html")
        msg["to"] = to
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self._retry_request(
            lambda: service.users().messages().send(userId="me", body={"raw": raw}).execute()
        )

    def get_account_email(self) -> str:
        """Get the Gmail account email address."""
        service = self._get_service()
        profile = self._retry_request(
            lambda: service.users().getProfile(userId="me").execute()
        )
        return profile.get("emailAddress", "")

    def _ensure_label(self, name: str) -> str:
        """Return the label ID for a given label name, creating it if needed."""
        if name in _LABEL_CACHE:
            return _LABEL_CACHE[name]

        service = self._get_service()

        if not _LABEL_CACHE:
            labels = (
                service.users()
                .labels()
                .list(userId="me")
                .execute()
                .get("labels", [])
            )
            for lbl in labels:
                _LABEL_CACHE[lbl["name"]] = lbl["id"]

        if name in _LABEL_CACHE:
            return _LABEL_CACHE[name]

        created = (
            service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        _LABEL_CACHE[name] = created["id"]
        return created["id"]
