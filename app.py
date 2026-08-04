"""Employer-facing Gradio interface for Joan Shirazi's digital twin."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import gradio as gr
from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

from context import TWIN_SYSTEM_PROMPT
from styles import CSS, EXAMPLES, FOOTER_HTML, HERO_HTML, JS, WELCOME_MESSAGE

load_dotenv(override=False)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama-3.1-8b-instant"
MAX_HISTORY_MESSAGES = 4
MAX_MESSAGE_CHARACTERS = 2_000
MAX_COMPLETION_TOKENS = 350

RATE_LIMIT_MESSAGE = (
    "I'm receiving more requests than the free Groq service currently allows. "
    "Please wait a moment and try again."
)
AUTH_MESSAGE = (
    "The digital twin is temporarily unavailable because its Groq service is not "
    "configured correctly. Please contact Joan using the links below."
)
UNAVAILABLE_MESSAGE = (
    "I couldn't reach the Groq service just now. Please try again shortly, or contact "
    "Joan using the email or LinkedIn links below."
)


class ConfigurationError(RuntimeError):
    """Raised when the Groq API is not configured safely."""


@dataclass(frozen=True)
class GroqSettings:
    model: str
    api_key: str


def get_groq_settings(environ: dict[str, str] | None = None) -> GroqSettings:
    """Resolve the Groq-only configuration."""

    env = os.environ if environ is None else environ
    api_key = env.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError("GROQ_API_KEY must be set.")

    return GroqSettings(
        model=DEFAULT_MODEL,
        api_key=api_key,
    )


def get_client(settings: GroqSettings) -> Groq:
    """Create a short-lived Groq client with bounded retries and request time."""

    return Groq(
        api_key=settings.api_key,
        timeout=30.0,
        max_retries=1,
    )


def _text_content(value: Any) -> str | None:
    """Return safe text from a Gradio message and ignore media/component payloads."""

    if not isinstance(value, str):
        return None
    value = value.strip()
    return value[:MAX_MESSAGE_CHARACTERS] if value else None


def build_messages(message: str, history: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    """Build a token-conscious message list for the Groq request."""

    bounded_history: list[dict[str, str]] = []
    for item in (history or [])[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            continue
        content = _text_content(item.get("content"))
        if content:
            bounded_history.append({"role": item["role"], "content": content})

    user_message = _text_content(message)
    if not user_message:
        return [{"role": "system", "content": TWIN_SYSTEM_PROMPT}, *bounded_history]

    return [
        {"role": "system", "content": TWIN_SYSTEM_PROMPT},
        *bounded_history,
        {"role": "user", "content": user_message},
    ]


def chat(message: str, history: list[dict[str, Any]] | None) -> str:
    """Answer one chat turn without storing visitor data or invoking local tools."""

    try:
        settings = get_groq_settings()
        client = get_client(settings)
        response = client.chat.completions.create(
            model=settings.model,
            messages=build_messages(message, history),
            max_completion_tokens=MAX_COMPLETION_TOKENS,
        )
        content = response.choices[0].message.content
        return content.strip() if content else UNAVAILABLE_MESSAGE
    except ConfigurationError:
        logger.exception("Groq configuration is invalid")
        return AUTH_MESSAGE
    except RateLimitError:
        logger.warning("Groq rate limit reached")
        return RATE_LIMIT_MESSAGE
    except AuthenticationError:
        logger.exception("Groq authentication failed")
        return AUTH_MESSAGE
    except (APITimeoutError, APIConnectionError):
        logger.warning("Groq connection failed", exc_info=True)
        return UNAVAILABLE_MESSAGE
    except APIStatusError:
        logger.warning("Groq returned an API error", exc_info=True)
        return UNAVAILABLE_MESSAGE
    except (AttributeError, IndexError, TypeError, ValueError):
        logger.exception("Groq returned an unexpected response")
        return UNAVAILABLE_MESSAGE


def build_demo() -> gr.Blocks:
    """Build the scoped, accessible Gradio application."""

    with gr.Blocks(
        analytics_enabled=False,
        title="Joan Shirazi — Digital Twin",
    ) as demo:
        with gr.Column(elem_classes=["twin-app"]):
            gr.HTML(HERO_HTML)

            chatbot = gr.Chatbot(
                show_label=False,
                placeholder=WELCOME_MESSAGE,
                height=460,
                layout="bubble",
                buttons=["copy"],
                feedback_options=None,
                sanitize_html=True,
                elem_id="twin-chatbot",
            )
            textbox = gr.Textbox(
                placeholder="Ask about Joan's experience or current Agentic AI work...",
                container=False,
                lines=1,
                max_lines=4,
                submit_btn="Send",
                elem_id="twin-input",
            )
            gr.ChatInterface(
                fn=chat,
                chatbot=chatbot,
                textbox=textbox,
                examples=EXAMPLES,
                example_labels=[
                    "Career overview",
                    "Agentic AI skills",
                    "Technical strengths",
                    "Contact Joan",
                ],
                run_examples_on_click=True,
                flagging_mode="never",
                analytics_enabled=False,
                autofocus=True,
                autoscroll=True,
                show_progress="minimal",
                concurrency_limit=1,
                api_visibility="private",
                save_history=False,
            )

            gr.HTML(FOOTER_HTML)

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch(css=CSS, js=JS, theme=gr.themes.Base())
