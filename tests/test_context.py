from pathlib import Path
import re

import context
import styles


ROOT = Path(__file__).resolve().parents[1]


def test_prompt_has_grounded_status_and_unknown_answer_behavior():
    prompt = context.TWIN_SYSTEM_PROMPT
    assert "Preserve the status of every fact" in prompt
    assert "completed projects from active" in prompt
    assert "Never imply that the thesis prototype" in prompt
    assert "If the answer is not in the supplied context" in prompt
    assert "Politely steer unrelated" in prompt
    assert "Never ask for, collect, record" in prompt


def test_approved_contact_links_are_visible_and_complete():
    prompt = context.TWIN_SYSTEM_PROMPT
    for value in (context.EMAIL, context.LINKEDIN_URL, context.GITHUB_URL):
        assert value in prompt

    for markup in (styles.HERO_HTML, styles.FOOTER_HTML):
        assert f"mailto:{context.EMAIL}" in markup
        assert context.LINKEDIN_URL in markup
        assert context.GITHUB_URL in markup


def test_private_source_contacts_are_not_in_production_text():
    production_text = "\n".join(
        (ROOT / filename).read_text(encoding="utf-8")
        for filename in ("app.py", "context.py", "styles.py", "summary.txt")
    )
    phone_like_values = re.findall(r"\+?\d[\d\s().-]{8,}\d", production_text)
    email_values = set(
        re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", production_text)
    )
    assert phone_like_values == []
    assert email_values == {context.EMAIL}
    assert "Never reveal a phone number" in context.TWIN_SYSTEM_PROMPT
    assert "thesis-supervisor contact details" in context.TWIN_SYSTEM_PROMPT


def test_resume_is_authoritative_for_career_timeline():
    summary = context.PROFILE_SUMMARY
    assert "AI Engineer and Data Scientist" in summary
    assert "more than five years" in summary
    assert "Siemens Financial Services (SFS)" in summary
    assert "October 2025 to current" in summary
    assert "Remotoco" in summary
    assert "Head of AI — Talent Matching Systems" in summary
    assert "January 2023 to March 2025" in summary
    assert "February 2021 to March 2023" in summary
    assert "July 2020 to February 2021" in summary
    assert "seven million rows daily" in summary
    assert "more than 150 fintech clients" in summary


def test_summary_contains_current_engineering_skills_and_education():
    summary = context.PROFILE_SUMMARY
    expected_skills = (
        "OpenAI API and Agents SDK",
        "CrewAI",
        "LangChain",
        "LangGraph",
        "AutoGen",
        "FastMCP",
        "retrieval-augmented generation (RAG)",
        "Qdrant",
        "C#",
        "TypeScript",
        "Flask",
        "PostgreSQL",
        "Redis",
        "Kafka",
        "GitHub Actions",
        "PyTest",
    )
    for skill in expected_skills:
        assert skill in summary

    assert "M.Sc. Data Science" in summary
    assert "B.Sc. Computer Science" in summary
    assert "English: C1" in summary
    assert "German: A2" in summary


def test_thesis_is_active_grounded_and_not_claimed_complete():
    summary = context.PROFILE_SUMMARY
    assert "Active master's thesis" in summary
    assert "AI-assisted Analysis and Explanation of Optimization Models" in summary
    assert "MILP or MINLP" in summary
    assert "irreducible infeasible subsystems (IIS)" in summary
    assert "grounded in verifiable model and solver information" in summary
    assert "active or planned thesis objectives, not confirmed milestones" in summary
    assert "has not claimed that the literature review" in summary
    assert "Do not convert thesis objectives into claimed progress" in context.TWIN_SYSTEM_PROMPT


def test_only_resume_featured_projects_are_described_as_completed():
    summary = context.PROFILE_SUMMARY
    assert "Completed featured projects" in summary
    assert "Digital Twin — AI Digital Twin" in summary
    assert "n8n Stock Portfolio Assistant" in summary
    assert "should not be described as completed featured portfolio projects" in summary


def test_notification_and_pdf_runtime_infrastructure_are_absent():
    assert not (ROOT / "tools.py").exists()
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "requests" not in requirements.splitlines()
    assert "openai" not in requirements.lower()
    assert "pypdf" not in requirements.lower()
    assert "groq==" in requirements.lower()

    runtime_source = "\n".join(
        (ROOT / filename).read_text(encoding="utf-8")
        for filename in ("app.py", "context.py")
    )
    assert ".pdf" not in runtime_source.lower()
    assert "PUSHOVER_" not in runtime_source
    assert "record_user_details" not in runtime_source
    assert "record_unknown_question" not in runtime_source
    assert "OPENAI_API_KEY" not in runtime_source
    assert "AI_PROVIDER" not in runtime_source


def test_private_profile_documents_are_ignored_and_untracked_locally():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*[Rr]esume*.pdf" in gitignore
    assert "*[Tt]hesis*.pdf" in gitignore
    assert not (ROOT / "JOAN_SHIRAZI_Resume.pdf").exists()
    assert not (
        ROOT / "04_ai_assisted_analysis_and_explanation_of_optimization_models.pdf"
    ).exists()
    assert (ROOT / "linkedin.pdf").exists()
