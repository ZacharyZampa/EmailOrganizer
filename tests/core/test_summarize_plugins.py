from lib.application import summarizer
from lib.domain.email_summarizer import EmailSummarizer


def test_summarize_with_plugins_uses_registered_summarizers():
    class TestSummarizer(EmailSummarizer):
        def can_handle(self, category: str, email_data: dict) -> bool:
            return category == "test"

        def summarize(self, email_data: dict, context: dict) -> str:
            return "Custom test summary"

        def get_priority(self) -> int:
            return 100

    summarizer.register_summarizer(TestSummarizer())

    email_data = {
        "subject": "Test",
        "sender": "test@example.com",
        "body": "Test body",
        "snippet": "Test",
    }

    result = summarizer.summarize_with_plugins("test", email_data, {})

    assert result == "Custom test summary"


def test_summarize_with_plugins_respects_priority():
    class LowPrioritySummarizer(EmailSummarizer):
        def can_handle(self, category: str, email_data: dict) -> bool:
            return True

        def summarize(self, email_data: dict, context: dict) -> str:
            return "Low priority"

        def get_priority(self) -> int:
            return 10

    class HighPrioritySummarizer(EmailSummarizer):
        def can_handle(self, category: str, email_data: dict) -> bool:
            return True

        def summarize(self, email_data: dict, context: dict) -> str:
            return "High priority"

        def get_priority(self) -> int:
            return 90

    summarizer.register_summarizer(LowPrioritySummarizer())
    summarizer.register_summarizer(HighPrioritySummarizer())

    email_data = {"subject": "Test", "sender": "test@example.com", "body": "Test", "snippet": "Test"}
    result = summarizer.summarize_with_plugins("any", email_data, {})

    assert result == "High priority"
