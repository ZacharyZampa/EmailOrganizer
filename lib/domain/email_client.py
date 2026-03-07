"""
Abstract interface for email clients.

This allows swapping between different email providers (Gmail, Outlook, etc.)
without changing the core processing logic.
"""

from abc import ABC, abstractmethod
from typing import Any


class EmailClient(ABC):
    """Abstract base class for email clients."""

    @abstractmethod
    def get_recent_messages(self, days: int = 3) -> list[dict[str, Any]]:
        """
        Fetch recent messages.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of message metadata dicts with at least 'id' field
        """
        pass

    @abstractmethod
    def get_message(self, msg_id: str) -> dict[str, Any]:
        """
        Fetch full message details.
        
        Args:
            msg_id: Message identifier
            
        Returns:
            Full message dict with headers and body
        """
        pass

    @abstractmethod
    def get_stale_messages(self, days: int = 30, max_results: int = 50) -> list[dict[str, Any]]:
        """
        Fetch old messages still in inbox.
        
        Args:
            days: Age threshold in days
            max_results: Maximum number of messages to return (0 = fetch all)
            
        Returns:
            List of message metadata dicts
        """
        pass

    @abstractmethod
    def add_labels(self, msg_id: str, labels: list[str]) -> None:
        """
        Add labels/tags to a message.
        
        Args:
            msg_id: Message identifier
            labels: List of label names to add
        """
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, html: str) -> None:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML body content
        """
        pass

    @abstractmethod
    def get_account_email(self) -> str:
        """
        Get the email address of the authenticated account.
        
        Returns:
            Email address string
        """
        pass
