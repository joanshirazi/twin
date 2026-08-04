from types import SimpleNamespace

import pytest

import app


class FakeCompletions:
    def __init__(self, content="A concise professional answer.", error=None):
        self.content = content
        self.error = error
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


def configured_settings():
    return app.GroqSettings(
        model="llama-3.1-8b-instant",
        api_key="test-key",
    )


def test_groq_is_the_only_configuration():
    settings = app.get_groq_settings(
        {
            "GROQ_API_KEY": "groq-key",
            "AI_PROVIDER": "openai",
            "AI_MODEL": "paid-model",
            "OPENAI_API_KEY": "paid-key",
        }
    )
    assert settings.model == "llama-3.1-8b-instant"

    with pytest.raises(app.ConfigurationError, match="GROQ_API_KEY"):
        app.get_groq_settings({})


def test_groq_model_cannot_be_overridden_by_environment():
    settings = app.get_groq_settings(
        {"GROQ_API_KEY": "groq-key", "GROQ_MODEL": "larger-model"}
    )
    assert settings.model == app.DEFAULT_MODEL


def test_build_messages_bounds_history_and_ignores_non_text_content():
    history = [
        {"role": "user", "content": f"message {index}"}
        for index in range(app.MAX_HISTORY_MESSAGES + 3)
    ]
    history.append({"role": "assistant", "content": {"path": "ignored.png"}})

    messages = app.build_messages("latest question", history)

    assert messages[0]["role"] == "system"
    assert messages[-1] == {"role": "user", "content": "latest question"}
    assert len(messages) <= app.MAX_HISTORY_MESSAGES + 2
    assert all(isinstance(item["content"], str) for item in messages)


def test_chat_returns_provider_response(monkeypatch):
    completions = FakeCompletions("  **Professional answer**  ")
    monkeypatch.setattr(app, "get_groq_settings", configured_settings)
    monkeypatch.setattr(app, "get_client", lambda settings: FakeClient(completions))

    result = app.chat("What is your background?", [])

    assert result == "**Professional answer**"
    assert completions.kwargs["model"] == "llama-3.1-8b-instant"
    assert completions.kwargs["max_completion_tokens"] == app.MAX_COMPLETION_TOKENS
    assert "tools" not in completions.kwargs


def test_chat_returns_clear_rate_limit_message(monkeypatch):
    class FakeRateLimitError(Exception):
        pass

    monkeypatch.setattr(app, "RateLimitError", FakeRateLimitError)
    monkeypatch.setattr(app, "get_groq_settings", configured_settings)
    monkeypatch.setattr(
        app,
        "get_client",
        lambda settings: FakeClient(FakeCompletions(error=FakeRateLimitError())),
    )

    assert app.chat("Hello", []) == app.RATE_LIMIT_MESSAGE


def test_chat_returns_clear_connection_message(monkeypatch):
    class FakeConnectionError(Exception):
        pass

    monkeypatch.setattr(app, "APIConnectionError", FakeConnectionError)
    monkeypatch.setattr(app, "get_groq_settings", configured_settings)
    monkeypatch.setattr(
        app,
        "get_client",
        lambda settings: FakeClient(FakeCompletions(error=FakeConnectionError())),
    )

    assert app.chat("Hello", []) == app.UNAVAILABLE_MESSAGE


def test_chat_returns_configuration_message_without_a_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert app.chat("Hello", []) == app.AUTH_MESSAGE


def test_demo_builds_without_api_credentials():
    assert isinstance(app.demo, app.gr.Blocks)
