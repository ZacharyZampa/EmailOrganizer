from __future__ import annotations

from dataclasses import dataclass, field

from lib.domain.llm_provider import LLMProvider


@dataclass
class FakeLLMProvider(LLMProvider):
    responses: dict[str, str] = field(default_factory=dict)
    default_response: str = ""
    calls: list[tuple[str, str | None]] = field(default_factory=list)

    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        self.calls.append((prompt, system_prompt))

        for needle, response in self.responses.items():
            if needle in prompt:
                return response

        if self.default_response:
            return self.default_response

        if "Return ONLY valid JSON" in prompt and '"category"' in prompt and '"priority"' in prompt:
            return '{"category": "work", "priority": 3}'

        if "Summarize this email" in prompt:
            return "Summary."

        if "Extract the most interesting items" in prompt:
            return "- Item 1\n- Item 2\n- Item 3"

        return ""

    def is_available(self) -> bool:
        return True
