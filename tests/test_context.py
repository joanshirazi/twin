from pathlib import Path

import context
import styles


ROOT = Path(__file__).resolve().parents[1]


def test_prompt_has_only_approved_contact_behavior():
    prompt = context.TWIN_SYSTEM_PROMPT
    assert f"mailto:{context.EMAIL}" in prompt
    assert context.LINKEDIN_URL in prompt
    assert "Never ask for, collect, record" in prompt
    assert "If the answer is not in the supplied context" in prompt
    assert "Politely steer unrelated" in prompt


def test_approved_contact_links_are_permanently_visible():
    for markup in (styles.HERO_HTML, styles.FOOTER_HTML):
        assert f"mailto:{context.EMAIL}" in markup
        assert context.LINKEDIN_URL in markup


def test_summary_lists_agentic_ai_as_current_skills():
    summary = context.PROFILE_SUMMARY
    assert "Established experience" in summary
    assert "Agentic AI engineering skills" in summary
    assert "current Agentic AI engineering skills" in summary
    assert "OpenAI Agents SDK" in summary
    assert "CrewAI" in summary
    assert "LangChain" in summary
    assert "LangGraph" in summary
    assert "AutoGen" in summary
    assert "Model Context Protocol (MCP)" in summary
    assert "currently learning" not in summary.lower()
    assert "growing, hands-on skills" not in summary.lower()


def test_notification_infrastructure_is_not_part_of_production_code():
    assert not (ROOT / "tools.py").exists()
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "requests" not in requirements.splitlines()
    assert "openai" not in requirements.lower()
    assert "pypdf" not in requirements.lower()
    assert "groq==" in requirements.lower()

    production_source = "\n".join(
        (ROOT / filename).read_text(encoding="utf-8")
        for filename in ("app.py", "context.py", "styles.py")
    )
    assert "PUSHOVER_" not in production_source
    assert "record_user_details" not in production_source
    assert "record_unknown_question" not in production_source
    assert "OPENAI_API_KEY" not in production_source
    assert "AI_PROVIDER" not in production_source
