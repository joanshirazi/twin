# Joan Shirazi — Digital Twin

An employer-facing AI profile built with Gradio. It answers professional questions
about Joan's career, education, professional skills, and Agentic AI project work. The
app does not collect or store visitor contact details; it directs visitors
to Joan's public email and LinkedIn profile.

## Local setup

Python 3.12.11 and all direct dependencies are pinned for reproducible Render and CI
builds.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:GROQ_API_KEY = "your-key"
python app.py
```

Copying `.env.example` to `.env` is also supported for local development. `.env`
files are ignored and must never be committed.

## Groq configuration

Groq is the application's only AI provider. Set `GROQ_API_KEY`. The app fixes the
model to the fast, compact `llama-3.1-8b-instant` so a deployment variable cannot
silently select a larger model.

The prompt, four-message history window, 2,000-character message limit, 350-token
response ceiling, and single-request concurrency limit keep free-tier token usage
bounded. Enable Zero Data Retention in the GroqCloud Data Controls page before
production use.

## Tests

```powershell
python -m pytest
python -m compileall -q app.py context.py styles.py tests
```

Tests mock all AI requests and do not require API keys.

## Render rollout

Render currently deploys `master`, so implementation and review should happen on a
feature branch. Before merging:

1. Add `GROQ_API_KEY` to the Render service.
2. Set Render Auto-Deploy to **After CI Checks Pass**.
3. Merge only after GitHub Actions passes.
4. Smoke-test career questions, Agentic AI questions, error states, and both contact
   links on desktop and mobile.

Remove the obsolete `AI_PROVIDER`, `AI_MODEL`, `GROQ_MODEL`, and `OPENAI_API_KEY`
variables from Render. The retired mobile-notification variables can also be removed
because this version has no notification, form, database, analytics, or
visitor-contact storage path.
