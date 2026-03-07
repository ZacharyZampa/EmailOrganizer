from lib.application import summarizer


def test_categorize_email_valid_json_normalises_and_clamps(monkeypatch):
    def fake_chat(prompt: str, system_prompt: str | None = None) -> str:
        return '{"category": "Work", "priority": 10}'

    monkeypatch.setattr(summarizer, "_chat", fake_chat)

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "work"
    assert result["priority"] == 5


def test_categorize_email_handles_markdown_fences(monkeypatch):
    def fake_chat(prompt: str, system_prompt: str | None = None) -> str:
        return "```json\n{\"category\": \"newsletter\", \"priority\": 2}\n```"

    monkeypatch.setattr(summarizer, "_chat", fake_chat)

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "newsletter"
    assert result["priority"] == 2


def test_categorize_email_falls_back_on_bad_json(monkeypatch):
    def fake_chat(prompt: str, system_prompt: str | None = None) -> str:
        return "this is not json"

    monkeypatch.setattr(summarizer, "_chat", fake_chat)

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "other"
    assert result["priority"] == 3


def test_summarize_newsletter_truncates_and_marks_long_bodies(monkeypatch):
    captured = {}

    def fake_chat(prompt: str, system_prompt: str | None = None) -> str:
        captured["prompt"] = prompt
        return "ok"

    monkeypatch.setattr(summarizer, "_chat", fake_chat)

    long_text = "x" * (summarizer.MAX_BODY_CHARS + 100)
    summarizer.summarize_newsletter(long_text, ["ai", "python"])

    prompt = captured["prompt"]
    assert "[... newsletter truncated for summarization ...]" in prompt




def test_summarize_with_plugins_uses_registered_summarizers():
    """Test that custom summarizers can be registered and used."""
    from lib.domain.email_summarizer import EmailSummarizer
    
    class TestSummarizer(EmailSummarizer):
        def can_handle(self, category: str, email_data: dict) -> bool:
            return category == "test"
        
        def summarize(self, email_data: dict, context: dict) -> str:
            return "Custom test summary"
        
        def get_priority(self) -> int:
            return 100
    
    # Register custom summarizer
    test_summarizer = TestSummarizer()
    summarizer.register_summarizer(test_summarizer)
    
    # Test it gets used
    email_data = {"subject": "Test", "sender": "test@example.com", "body": "Test body", "snippet": "Test"}
    result = summarizer.summarize_with_plugins("test", email_data, {})
    
    assert result == "Custom test summary"


def test_summarize_with_plugins_respects_priority():
    """Test that higher priority summarizers are checked first."""
    from lib.domain.email_summarizer import EmailSummarizer
    
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
    
    # Register in reverse order
    summarizer.register_summarizer(LowPrioritySummarizer())
    summarizer.register_summarizer(HighPrioritySummarizer())
    
    email_data = {"subject": "Test", "sender": "test@example.com", "body": "Test", "snippet": "Test"}
    result = summarizer.summarize_with_plugins("any", email_data, {})
    
    # High priority should win
    assert result == "High priority"
