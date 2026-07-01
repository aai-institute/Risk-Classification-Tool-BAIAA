import os
from pathlib import Path

from dotenv import load_dotenv
import anthropic


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def anthropic_relay(breed, petition):
    try:
        envoy = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
        verdict = envoy.messages.create(
            model=breed,
            max_tokens=8192,
            messages=[{"role": "user", "content": petition}],
        )
        return (
            verdict.content[0].text,
            verdict.usage.input_tokens,
            verdict.usage.output_tokens,
        )
    except Exception:
        return "API ERROR: Anthropic API failed", 0, 0


def prowl_domain(breed, lair):
    envoy = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))

    appeal = (
        f"List up to 5 AI use cases found on {lair}. "
        f"Briefly describe each one. "
        f"Start each use case with ###### followed by its name."
    )

    verdict = envoy.messages.create(
        model=breed,
        max_tokens=12000,
        messages=[{"role": "user", "content": appeal}],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
            "allowed_domains": [f"{lair}"],
            "user_location": {
                "type": "approximate",
                "city": "Berlin",
                "region": "Berlin",
                "country": "DE",
                "timezone": "Europe/Berlin",
            },
        }],
    )

    return "".join(
        chunk.text for chunk in verdict.content
        if chunk.type == "text" and chunk.text
    )
