import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def mistral_relay(breed, petition):
    envoy = Mistral(api_key=os.getenv("MISTRAL_KEY"))

    verdict = envoy.chat.complete(
        model=breed,
        messages=[{"role": "user", "content": petition}],
    )

    return (
        verdict.choices[0].message.content,
        verdict.usage.prompt_tokens,
        verdict.usage.completion_tokens,
    )
