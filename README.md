Local LLM Email Organizer

A local-first, modular email intelligence tool that uses a local LLM to:
	•	categorize emails
	•	prioritize messages
	•	summarize newsletters
	•	detect promotions/spam
	•	identify high-volume senders

All processing runs locally on your machine using an LLM and a modern open model like Qwen3 14B.

No email content is sent to external APIs, unless you want it to of course.

**Fully Modular:** Swap out the LLM provider, email client, or database with your own implementations. See [DEVELOPER.md](DEVELOPER.md) for details.

⸻

✨ Features
	•	📂 Automatic categorization
	•	work
	•	personal
	•	finance
	•	newsletter
	•	promo
	•	spam
	•	⚡ Priority scoring
	•	ranks emails 1–5
	•	📰 Newsletter summarization
	•	📊 High-volume sender detection
	•	flags newsletters cluttering your inbox
	•	🧹 Stale email cleanup suggestions
	•	🔒 Fully local LLM processing
	•	🚀 Fast on Apple Silicon
	•	tested on M4 Pro
	•	🔌 Pluggable architecture
	•	swap LLM providers (OpenAI, Anthropic, etc.)
	•	swap email clients (Outlook, ProtonMail, etc.)

⸻

🏗 Architecture

Email API
   │
   ▼
Fetch recent emails
   │
   ▼
Local LLM (LM Studio)
   │
   ▼
Categorization + priority
   │
   ├── newsletters → summary
   │
   ▼
Structured JSON output


⸻

🧠 Model

Recommended model:

Qwen3-14B-Instruct

Why:
	•	excellent instruction following
	•	strong text classification
	•	reliable JSON output
	•	runs well locally on Macs

Optional alternatives:
	•	Mistral Nemo 12B
	•	DeepSeek R1 Distill 14B

⸻

💻 Requirements
	•	Python 3.10+
	•	Gmail API credentials
	•	LM Studio running locally
	•	Apple Silicon Mac recommended

Works best on:
	•	M3 Pro
	•	M4 Pro
	•	24–32GB RAM

⸻

⚙️ Setup

1️⃣ Clone the repo

git clone https://github.com/ZacharyZampa/EmailOrganizer.git


⸻

2️⃣ Install dependencies

pip install -r requirements.txt



⸻

3️⃣ Setup Gmail API

Create credentials in:

Google Cloud Console

Enable:

Gmail API

Download:

credentials.json

Place it in the project root.

First run will generate:

token.json


⸻

4️⃣ Install and run LM Studio

Install:

👉 https://lmstudio.ai

Load a model such as:

Qwen3-14B-Instruct

Enable the OpenAI compatible API.

Default endpoint:

http://localhost:1234/v1


⸻

5️⃣ Configure environment

Example:

LM_MODEL=qwen3-14b
LM_ENDPOINT=http://localhost:1234/v1


⸻

▶️ Run

python main.py

The script will:
	1.	Fetch recent Gmail messages
	2.	Send email content to the local LLM
	3.	Return structured classifications

Example output:

{
  "category": "newsletter",
  "priority": 2,
  "summary": "Weekly tech roundup covering AI releases and startup news."
}


⸻

🧾 Example Prompt

The model receives a prompt like:

Categorize this email.

Return JSON:

{
 "category": "work|personal|finance|newsletter|promo|spam",
 "priority": 1-5,
 "summary": ""
}

EMAIL:
<email text>

/no_think

⸻

🔐 Privacy

All email content stays local.
	•	no external API
	•	no cloud inference
	•	no third-party logging

⸻

📄 License

MIT License
