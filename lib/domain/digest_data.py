"""
Data structures for email digest generation.

These dataclasses define the structure of digest data,
allowing custom HTML templates to be used.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DigestEmail:
    """A single email in the digest."""
    gmail_id: str
    type: str
    title: str
    sender: str
    summary: str
    priority: int


@dataclass
class StaleEmail:
    """An old email that may need cleanup."""
    gmail_id: str
    sender: str
    subject: str
    category: str
    priority: int
    processed_at: Optional[str]
    action: str
    suggested_category: Optional[str]


@dataclass
class HighVolumeSender:
    """A sender with high email volume."""
    sender: str
    total: int
    categories: dict[str, int]
    is_newsletter: bool


@dataclass
class DigestData:
    """Complete digest data structure."""
    emails: list[DigestEmail]
    stale_emails: list[StaleEmail]
    high_volume_senders: list[HighVolumeSender]
    thread_base: str
