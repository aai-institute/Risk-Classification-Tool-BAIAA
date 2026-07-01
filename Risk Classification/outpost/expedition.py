import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def gemini_relay(breed, petition):
    genai.configure(api_key=os.getenv("GEMINI_KEY"))

    contraption = genai.GenerativeModel(
        model_name=breed,
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
    )

    verdict = contraption.start_chat(history=[]).send_message(petition)

    return (
        verdict.text,
        verdict.usage_metadata.prompt_token_count,
        verdict.usage_metadata.candidates_token_count,
    )
