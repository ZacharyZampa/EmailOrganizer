from lib.adapters.summarizers.builtin_summarizers import (
    NewsletterSummarizer,
    StandardEmailSummarizer,
    FallbackSummarizer,
    PRIORITY_NEWSLETTER,
    PRIORITY_STANDARD,
    PRIORITY_FALLBACK,
)

from tests.fakes.fake_llm_provider import FakeLLMProvider


def test_builtin_summarizer_can_handle_and_priorities():
    llm = FakeLLMProvider()

    newsletter = NewsletterSummarizer(llm)
    standard = StandardEmailSummarizer(llm)
    fallback = FallbackSummarizer(llm)

    assert newsletter.can_handle("newsletter", {}) is True
    assert standard.can_handle("work", {}) is True
    assert standard.can_handle("promo", {}) is False
    assert fallback.can_handle("anything", {}) is True

    assert newsletter.get_priority() == PRIORITY_NEWSLETTER
    assert standard.get_priority() == PRIORITY_STANDARD
    assert fallback.get_priority() == PRIORITY_FALLBACK


def test_fallback_summarizer_does_not_call_llm():
    llm = FakeLLMProvider()
    fallback = FallbackSummarizer(llm)

    result = fallback.summarize({"snippet": "Hello", "sender": "a@b.com"}, {})

    assert "a@b.com" in result
    assert llm.calls == []
