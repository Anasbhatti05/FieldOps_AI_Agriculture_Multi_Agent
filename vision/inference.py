import base64
import json
import os
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from groq import Groq


def _setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "")
    if value.strip():
        return value
    try:
        return str(st.secrets.get(name, default))
    except StreamlitSecretNotFoundError:
        return default


def vision_enabled() -> bool:
    return bool(_setting("GROQ_API_KEY")) and _setting("GROQ_VISION_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def inspect_crop_image(image_bytes: bytes | None) -> dict[str, str]:
    if not image_bytes:
        return {
            "status": "needs_review",
            "finding": "No crop photo was supplied; visible crop condition was not assessed.",
            "confidence": "low",
        }

    api_key = _setting("GROQ_API_KEY")
    if not api_key or not vision_enabled():
        return {
            "status": "needs_review",
            "finding": "Photo received but not sent to an AI service. Enable private Groq vision screening only after reviewing API cost and access.",
            "confidence": "low",
        }

    model = _setting("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    image_data = base64.b64encode(image_bytes).decode("ascii")
    prompt = (Path(__file__).parents[1] / "prompts" / "vision_screening.txt").read_text(encoding="utf-8")
    response = Groq(api_key=api_key).chat.completions.create(
        model=model,
        temperature=0,
        max_completion_tokens=350,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Screen this crop photo cautiously. Mention only visible signs."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                ],
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"visible_signs": content, "possible_causes": "Unknown", "next_check": "Ask a local crop adviser.", "confidence": "low"}

    return {
        "status": "needs_review",
        "finding": (
            f"Visible signs: {result.get('visible_signs', 'unclear')}. "
            f"Possible causes to check: {result.get('possible_causes', 'uncertain')}."
        ),
        "confidence": "low",
        "next_check": str(result.get("next_check", "Compare with a local crop adviser.")),
    }