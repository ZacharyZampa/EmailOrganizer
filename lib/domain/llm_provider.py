"""
Abstract interface for LLM providers.

This allows swapping between different LLM backends (LM Studio, OpenAI, Anthropic, etc.)
without changing the core email processing logic.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send a chat completion request to the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Returns:
            The LLM's response text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available and ready."""
        pass
