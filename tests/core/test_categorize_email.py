from lib.application import summarizer
from tests.fakes.fake_llm_provider import FakeLLMProvider


def test_categorize_email_valid_json_normalises_and_clamps():
    summarizer.set_llm_provider(FakeLLMProvider(default_response='{"category": "Work", "priority": 10}'))

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "work"
    assert result["priority"] == 5


def test_categorize_email_handles_markdown_fences():
    summarizer.set_llm_provider(
        FakeLLMProvider(default_response="```json\n{\"category\": \"newsletter\", \"priority\": 2}\n```")
    )

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "newsletter"
    assert result["priority"] == 2


def test_categorize_email_falls_back_on_bad_json():
    summarizer.set_llm_provider(FakeLLMProvider(default_response="this is not json"))

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "other"
    assert result["priority"] == 3


def test_categorize_email_unknown_category_becomes_other():
    summarizer.set_llm_provider(FakeLLMProvider(default_response='{"category": "Urgent", "priority": 2}'))

    result = summarizer.categorize_email("dummy email text")

    assert result["category"] == "other"
    assert result["priority"] == 2
