"""
Abstract interface for email summarizers.

This allows adding custom summarization strategies for different email types
without modifying the core pipeline.
"""

from abc import ABC, abstractmethod
from typing import Optional


class EmailSummarizer(ABC):
    """Abstract base class for email summarizers."""

    @abstractmethod
    def can_handle(self, category: str, email_data: dict) -> bool:
        """
        Check if this summarizer can handle the given email.
        
        Args:
            category: Email category (work, newsletter, etc.)
            email_data: Dict with 'subject', 'sender', 'body', 'snippet'
            
        Returns:
            True if this summarizer should handle this email
        """
        pass

    @abstractmethod
    def summarize(self, email_data: dict, context: dict) -> str:
        """
        Generate a summary for the email.
        
        Args:
            email_data: Dict with 'subject', 'sender', 'body', 'snippet'
            context: Additional context (interests, config, etc.)
            
        Returns:
            Summary text
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """
        Get the priority of this summarizer (higher = checked first).
        
        Returns:
            Priority value (0-100)
        """
        pass
