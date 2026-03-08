# Developer Guide

## Architecture

This project follows **Hexagonal Architecture** (Ports and Adapters) for maximum modularity and testability.

### Structure

```
lib/
├── domain/                    # Core business logic & interfaces (ports)
│   ├── email_client.py       # Email provider interface
│   ├── llm_provider.py       # LLM provider interface
│   ├── digest_renderer.py   # Digest renderer interface
│   └── digest_data.py        # Data structures
│
├── application/               # Use cases & orchestration
│   ├── summarizer.py         # Email categorization logic
│   └── run.py                # Main pipeline orchestration
│
└── adapters/                  # External integrations (adapters)
    ├── email/
    │   └── gmail_client.py   # Gmail API implementation
    ├── llm/
    │   └── lm_studio_provider.py  # LM Studio implementation
    ├── storage/
    │   └── db.py             # SQLite implementation
    └── presentation/
        └── digest.py         # HTML renderer implementation
```

### Layers

**Domain Layer** - Pure business logic, no dependencies
- Defines interfaces (ports) for external systems
- Contains data structures and domain models

**Application Layer** - Use cases and workflows
- Orchestrates domain logic
- Depends only on domain interfaces

**Adapters Layer** - External system integrations
- Implements domain interfaces
- Can be swapped without changing core logic

#### 1. LLM Provider (`lib/domain/llm_provider.py`)

Swap out the local LLM for any other provider (OpenAI, Anthropic, etc.):

```python
from lib.domain.llm_provider import LLMProvider
from lib.application import summarizer

class MyCustomLLM(LLMProvider):
    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        # Your implementation
        pass
    
    def is_available(self) -> bool:
        # Check if your LLM is ready
        pass

# Use your custom LLM
summarizer.set_llm_provider(MyCustomLLM())
```

**Default Implementation:** `lib/adapters/llm/lm_studio_provider.py`

#### 2. Email Client (`lib/domain/email_client.py`)

Swap Gmail for Outlook, ProtonMail, or any other email provider:

```python
from lib.domain.email_client import EmailClient
from lib.application.run import main

class OutlookClient(EmailClient):
    def get_recent_messages(self, days: int = 3):
        # Your implementation
        pass
    
    def get_message(self, msg_id: str):
        # Your implementation
        pass
    
    # ... implement other methods

# Use your custom email client
main(email_client=OutlookClient())
```

**Default Implementation:** `lib/adapters/email/gmail_client.py`

#### 3. Email Summarizer (`lib/domain/email_summarizer.py`)

Add custom summarization logic for specific email types:

```python
from lib.domain.email_summarizer import EmailSummarizer
from lib.application import summarizer

class ReceiptSummarizer(EmailSummarizer):
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def can_handle(self, category: str, email_data: dict) -> bool:
        # Check if this is a receipt email
        subject = email_data.get("subject", "").lower()
        return category == "finance" and "receipt" in subject
    
    def summarize(self, email_data: dict, context: dict) -> str:
        # Custom summarization logic
        snippet = email_data.get("snippet", "")
        return f"Receipt: {snippet[:100]}"
    
    def get_priority(self) -> int:
        return 60  # Higher priority = checked first

# Register your custom summarizer
summarizer.register_summarizer(ReceiptSummarizer(llm_provider))
```

**Built-in Summarizers:** `lib/adapters/summarizers/builtin_summarizers.py`
- `NewsletterSummarizer` - Extracts interesting items
- `StandardEmailSummarizer` - General email summaries
- `FallbackSummarizer` - Default handler

### Module Structure

```
lib/
├── domain/                    # Interfaces & data models
│   ├── llm_provider.py
│   ├── email_client.py
│   ├── digest_renderer.py
│   └── digest_data.py
├── application/               # Business logic
│   ├── summarizer.py
│   └── run.py
└── adapters/                  # External integrations
    ├── email/gmail_client.py
    ├── llm/lm_studio_provider.py
    ├── storage/db.py
    └── presentation/digest.py
```

### Extending the System

#### Add a Custom Email Summarizer

Create a new summarizer for specific email types:

```python
# my_summarizers.py
from lib.domain.email_summarizer import EmailSummarizer

class EventInviteSummarizer(EmailSummarizer):
    def can_handle(self, category: str, email_data: dict) -> bool:
        subject = email_data.get("subject", "").lower()
        return "invite" in subject or "event" in subject
    
    def summarize(self, email_data: dict, context: dict) -> str:
        # Extract event details
        return f"Event invitation: {email_data['subject']}"
    
    def get_priority(self) -> int:
        return 70  # Check before standard summarizers

# Register it
from lib.application import summarizer
summarizer.register_summarizer(EventInviteSummarizer(llm_provider))
```

#### Add a New Email Category

Edit `lib/application/summarizer.py`:

```python
VALID_CATEGORIES = {
    "work", "personal", "finance", "newsletter", 
    "promo", "spam", "urgent"  # Add your category
}
```

Update the prompt in `categorize_email()` to include your new category.

#### Add a New Digest Section

Edit `lib/adapters/presentation/digest.py` and add a rendering function:

```python
def _render_my_section(data):
    # Generate HTML for your section
    return f"<div>{data}</div>"

def generate_digest(..., my_data=None):
    # Add your section to the digest
    my_section = _render_my_section(my_data or [])
```

#### Use a Different Database

Replace `lib/adapters/storage/db.py` with your own implementation. The interface is simple:

- `get_db()` returns a connection object
- Connection supports `.execute()` and `.commit()`
- Schema defined in `db.py`

### Configuration

All user-configurable settings are in `lib/config.py`:

- `LM_MODEL` - Which local model to use
- `INTERESTS` - Topics to extract from newsletters
- `PRIORITY_THRESHOLD` - Minimum priority for digest inclusion
- `EMAIL_ADDRESSES` - Where to send digests
- `VALID_CATEGORIES` - Email categories

### Testing

Tests use **fake adapters** (no external services) and **snapshot testing** for HTML output.

```
tests/
├── conftest.py              # Shared fixtures, auto-reset of summarizer state
├── fakes/
│   ├── fake_email_client.py # In-memory EmailClient implementation
│   └── fake_llm_provider.py # Deterministic LLMProvider implementation
├── core/
│   ├── test_categorize_email.py    # JSON parsing, normalization, fallbacks
│   ├── test_summarize_plugins.py   # Plugin dispatch, priority ordering
│   └── test_digest_data.py         # Dataclass construction
├── pipeline/
│   └── test_pipeline.py            # End-to-end through main() using fakes
├── adapters/
│   ├── test_builtin_summarizers.py # Newsletter/Standard/Fallback logic
│   ├── test_html_renderer.py        # Snapshot tests for HTML output
│   └── test_db.py                   # SQLite schema + round-trip
├── test_email_parsing.py           # get_body, get_header, process_message_metadata
└── test_db_queries.py              # save_email_to_db, get_high_volume_senders, etc.
```

#### Running tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Update HTML snapshots (when template changes)
pytest --snapshot-update
```

#### Pre-commit hooks

Tests run automatically before each commit via pre-commit:

```bash
# Install once
pip install pre-commit
pre-commit install

# Manual run
pre-commit run --all-files
```

#### Adding tests

- **Core logic**: Use `FakeLLMProvider` via `set_llm_provider()` in `tests/core/`
- **Pipeline**: Use `FakeEmailClient` + in-memory DB in `tests/pipeline/`
- **HTML changes**: Run `pytest --snapshot-update` to update snapshots
- **New adapters**: Import fakes from `tests.fakes`

### Contributing

When adding features:

1. Keep interfaces abstract and implementations separate
2. Add tests for new functionality
3. Update this guide if adding new extension points
4. Follow the existing code style (minimal, readable)

### Example: Adding OpenAI Support

```python
# lib/adapters/llm/openai_provider.py
from openai import OpenAI
from lib.domain.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        try:
            self.client.models.list()
            return True
        except:
            return False

# Usage in your code
from lib.application import summarizer
from lib.adapters.llm.openai_provider import OpenAIProvider

summarizer.set_llm_provider(OpenAIProvider(api_key="sk-..."))
```
