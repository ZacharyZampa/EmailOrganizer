# Hexagonal Architecture

This project follows **Hexagonal Architecture** (also known as Ports and Adapters) to ensure maximum modularity, testability, and maintainability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ADAPTERS (Outer Layer)                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Gmail API  │  │  LM Studio   │  │   SQLite     │      │
│  │   Adapter    │  │   Adapter    │  │   Adapter    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         │                  │                  │               │
│  ┌──────▼──────────────────▼──────────────────▼───────┐     │
│  │              DOMAIN (Core/Ports)                    │     │
│  │                                                      │     │
│  │  ┌────────────────┐  ┌────────────────┐           │     │
│  │  │ EmailClient    │  │  LLMProvider   │           │     │
│  │  │  Interface     │  │   Interface    │           │     │
│  │  └────────────────┘  └────────────────┘           │     │
│  │                                                      │     │
│  │  ┌────────────────┐  ┌────────────────┐           │     │
│  │  │DigestRenderer  │  │  DigestData    │           │     │
│  │  │  Interface     │  │   (Models)     │           │     │
│  │  └────────────────┘  └────────────────┘           │     │
│  │                                                      │     │
│  └──────────────────────────────────────────────────────┘     │
│                           │                                    │
│                           │                                    │
│  ┌────────────────────────▼──────────────────────────────┐   │
│  │           APPLICATION (Use Cases)                      │   │
│  │                                                         │   │
│  │  ┌──────────────┐         ┌──────────────┐           │   │
│  │  │ Summarizer   │         │  Pipeline    │           │   │
│  │  │  (Categorize │  ◄────► │ Orchestrator │           │   │
│  │  │  & Summarize)│         │   (run.py)   │           │   │
│  │  └──────────────┘         └──────────────┘           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Layers

### 1. Domain Layer (Core)
**Location:** `lib/domain/`

- Pure business logic with no external dependencies
- Defines interfaces (ports) for external systems
- Contains data models and domain entities
- **Principle:** The domain knows nothing about the outside world

**Files:**
- `email_client.py` - Port for email providers
- `llm_provider.py` - Port for LLM services
- `digest_renderer.py` - Port for output formatting
- `digest_data.py` - Domain models

### 2. Application Layer (Use Cases)
**Location:** `lib/application/`

- Orchestrates domain logic
- Implements business workflows
- Depends only on domain interfaces (not implementations)
- **Principle:** Application logic is independent of infrastructure

**Files:**
- `summarizer.py` - Email categorization and summarization logic
- `run.py` - Main pipeline orchestration

### 3. Adapters Layer (Infrastructure)
**Location:** `lib/adapters/`

- Implements domain interfaces
- Handles external system integration
- Can be swapped without changing core logic
- **Principle:** Adapters depend on domain, not vice versa

**Subdirectories:**
- `email/` - Email provider implementations (Gmail, etc.)
- `llm/` - LLM provider implementations (LM Studio, OpenAI, etc.)
- `storage/` - Database implementations (SQLite, etc.)
- `presentation/` - Output formatters (HTML, etc.)

## Benefits

### 1. **Testability**
- Core logic can be tested without external dependencies
- Easy to mock adapters for unit tests
- Integration tests only touch adapter layer

### 2. **Flexibility**
- Swap Gmail for Outlook without changing business logic
- Switch from LM Studio to OpenAI with one line
- Replace SQLite with PostgreSQL by swapping adapter

### 3. **Maintainability**
- Clear separation of concerns
- Changes to external APIs don't affect core logic
- Easy to understand and navigate

### 4. **Scalability**
- Add new adapters without modifying existing code
- Support multiple implementations simultaneously
- Easy to add new features

## Dependency Rule

**Dependencies point inward:**

```
Adapters → Application → Domain
```

- **Domain** has no dependencies
- **Application** depends only on Domain
- **Adapters** depend on Domain (and Application for orchestration)

**Never:**
- Domain depending on Application or Adapters
- Application depending on Adapters

## Example: Adding a New Adapter

Want to add Anthropic Claude support?

1. Create `lib/adapters/llm/anthropic_provider.py`
2. Implement `LLMProvider` interface from `lib/domain/llm_provider.py`
3. Use it: `summarizer.set_llm_provider(AnthropicProvider())`

**No changes needed to:**
- Domain layer
- Application layer
- Other adapters

This is the power of hexagonal architecture!
