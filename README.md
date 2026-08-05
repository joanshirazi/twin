# Joan Shirazi — Digital Twin

[![Validate digital twin](https://github.com/joanshirazi/twin/actions/workflows/ci.yml/badge.svg)](https://github.com/joanshirazi/twin/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An employer-facing AI profile built with Gradio and Groq. It answers questions
about Joan's career, technical skills, completed projects, and active master's
thesis while preserving the status of current, completed, and planned work.

## How it works

```text
Visitor question
      ↓
Gradio chat interface
      ↓
Static curated profile + bounded four-message history
      ↓
Groq GPT-OSS 120B with low hidden reasoning
      ↓
Concise professional answer
```

The application makes one model request per chat turn. It has no local tools,
database, analytics, notification service, visitor-contact form, or automatic
provider fallback.

## Curated professional knowledge

`summary.txt` is the application's only runtime source of career and project
facts. It contains a manually reviewed profile covering:

- AI engineering, data science, software, and automation experience;
- Siemens Financial Services, Remotoco, JNSQ Analytics, and i2c roles;
- Agentic AI, LLM engineering, machine learning, API, data, and cloud skills;
- the completed Digital Twin and n8n Stock Portfolio Assistant projects;
- Joan's active master's thesis on grounded AI-assisted explanation of existing
  mathematical optimization models and solver results;
- education, languages, availability, and approved public links.

The repository's existing `linkedin.pdf` is intentionally public archival source
material, but production code never reads or sends it to Groq. New resume and
thesis source documents stay outside the repository; relevant facts are curated
into `summary.txt` instead.

## Model and free-tier controls

Groq is the only AI provider. Set `GROQ_API_KEY`; the application fixes the model
to `openai/gpt-oss-120b` and never switches to a paid fallback.

Requests use low hidden reasoning, a four-message history window, a 2,000-character
message limit, a 500-token completion ceiling, a 30-second timeout, bounded retries,
and single-request concurrency. The static prompt prefix also allows Groq's
[automatic prompt caching](https://console.groq.com/docs/prompt-caching) to reduce
counted input tokens when cache hits occur.

Groq's published free limits can change, so verify the current values on its
[rate-limit page](https://console.groq.com/docs/rate-limits) and enable Zero Data
Retention in GroqCloud Data Controls before production use.

## Privacy

The only contact details the assistant may provide are:

- [Email](mailto:syed.joan@hotmail.com)
- [LinkedIn](https://www.linkedin.com/in/joan-shirazi)
- [GitHub](https://github.com/joanshirazi)

The assistant never asks for or stores visitor contact details. Phone numbers,
private resume data, and thesis-supervisor contact details are excluded from the
runtime profile and prompt.

## Local setup

Python 3.12.11 and all direct dependencies are pinned for reproducible Render and
CI builds.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:GROQ_API_KEY = "your-key"
python app.py
```

Copying `.env.example` to `.env` is also supported. `.env` files and private
profile source documents are ignored and must never be committed.

## Validation

```powershell
python -m pytest -q
python -m pip check
python -m compileall -q app.py context.py styles.py tests
```

Tests mock all model requests and therefore do not require an API key. They cover
model configuration, bounded conversation history, error handling, profile facts,
thesis status, approved contacts, and privacy invariants.

## Render deployment

Render deploys `master`. Configure the service with only `GROQ_API_KEY` for model
access and set Auto-Deploy to **After CI Checks Pass**. Before merging a release:

1. Confirm `openai/gpt-oss-120b` is enabled for the Groq project.
2. Require the GitHub Actions validation job to pass.
3. Smoke-test career, thesis, projects, follow-up, unknown-question, and contact
   prompts after deployment.
4. Roll back to Render's previous successful deployment if startup or chat checks
   fail.

## License

This project is available under the [MIT License](LICENSE).
