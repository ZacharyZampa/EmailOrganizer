"""
Example: Using OpenAI instead of LM Studio

Note example was AI Generated so take with a grain of salt

This shows how to swap the LLM provider to use OpenAI's API
instead of a local LM Studio instance.
"""

from openai import OpenAI
from lib.domain.llm_provider import LLMProvider
from lib.application import summarizer
from lib.application.run import main


class OpenAIProvider(LLMProvider):
    """OpenAI API implementation of LLMProvider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send chat completion to OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    def is_available(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False


if __name__ == "__main__":
    # Set your OpenAI API key
    api_key = "sk-..."  # Replace with your actual key
    
    # Configure the summarizer to use OpenAI
    summarizer.set_llm_provider(OpenAIProvider(api_key=api_key))
    
    # Run the main pipeline - everything else stays the same!
    main()
