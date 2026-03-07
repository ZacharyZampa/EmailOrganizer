"""
Abstract interface for digest renderers.

This allows swapping HTML templates or using different output formats
(plain text, markdown, etc.) without changing the core logic.
"""

from abc import ABC, abstractmethod
from lib.domain.digest_data import DigestData


class DigestRenderer(ABC):
    """Abstract base class for digest renderers."""

    @abstractmethod
    def render(self, data: DigestData) -> str:
        """
        Render digest data to output format.
        
        Args:
            data: DigestData containing all digest information
            
        Returns:
            Rendered output (HTML, plain text, etc.)
        """
        pass
