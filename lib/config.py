EMAIL_ADDRESSES = ["example@gmail.com"] ## TODO dedupe this and below keys

# Map each recipient email to the Gmail web UI thread base they use
# e.g. "https://mail.google.com/mail/u/0/#inbox/" or ".../u/1/#inbox/"
EMAIL_THREAD_BASES = {
    "example@gmail.com": "https://mail.google.com/mail/u/0/#inbox/",
}

INTERESTS = [
    "tech",
    "fitness",
    "travel"
]

PRIORITY_THRESHOLD = 3  # Include emails with priority >= this

# Gmail label configuration
GMAIL_DIGEST_LABEL = "AI/Digest"
GMAIL_CATEGORY_LABEL_PREFIX = "AI/Digest/"

# Email processing configuration
STALE_EMAIL_MAX_RESULTS = 0  # 0 = fetch all stale emails, or set a limit
HIGH_VOLUME_SENDER_THRESHOLD = 10  # Min emails to flag as high volume
MAX_BODY_CHARS = 12_000  # Max characters for newsletter summarization

# Gmail API rate limiting
GMAIL_API_REQUESTS_PER_SECOND = 5  # Max requests per second
GMAIL_API_RETRY_ATTEMPTS = 3  # Number of retry attempts
GMAIL_API_RETRY_DELAY = 1.0  # Initial retry delay in seconds

# LM Studio Local API
LM_BASE_URL = "http://localhost:1234/v1"
LM_API_KEY = "lm-studio"
LM_MODEL = "qwen3-14b"
LM_TEMPERATURE = 0.1             # Lower temperature for more focused outputs
LM_NO_THINK = "/no_think"        # Qwen3 thinking mode control

DB_PATH = "data/state.db"
