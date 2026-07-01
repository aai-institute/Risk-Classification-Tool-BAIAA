import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from crucible.foray import anthropic_relay
from crucible.index import TRAILER
from precinct.sentry import mistral_relay
from outpost.expedition import gemini_relay


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


class Conduit:
    def __init__(self, breed, payload, scroll, envoy):
        self.__breed = breed
        self.__payload = payload
        self.__scroll = scroll
        self.__envoy = envoy

    def swap_payload(self, payload):
        self.__payload = payload

    def relay(self, system_text=""):
        if system_text:
            self.__scroll.append({"role": "system", "content": system_text})

        self.__scroll.append({"role": "user", "content": self.__payload})

        try:
            satchel = {"model": self.__breed, "messages": self.__scroll}

            if self.__breed == "o3-mini":
                satchel["reasoning_effort"] = "high"
                satchel["max_completion_tokens"] = 8192
            elif self.__breed == "deepseek-reasoner":
                satchel["max_tokens"] = 8192
            elif self.__breed == "gpt-4o-search-preview":
                satchel["web_search_options"] = {
                    "user_location": {
                        "type": "approximate",
                        "approximate": {
                            "country": "DE",
                            "city": "Berlin",
                            "region": "Berlin",
                            "timezone": "Europe/Berlin",
                        },
                    },
                    "search_context_size": "high",
                }

            verdict = self.__envoy.chat.completions.create(**satchel)

            spoken = verdict.choices[0].message.content.strip()
            self.__scroll.append({"role": "assistant", "content": spoken})

            return [spoken, verdict.usage.prompt_tokens, verdict.usage.completion_tokens]

        except Exception as mishap:
            print(f"API Error: {mishap}")
            return [None, None]


def coax_oracle(banner, breed, petition, ledger, attempts=4, dwell=10):
    for round_no in range(attempts):
        try:
            if banner == "chatgpt":
                envoy = OpenAI(api_key=os.getenv("OpenAI_KEY"), max_retries=5)
                spoken, influx, outflux = Conduit(breed, petition, [], envoy).relay()
            elif banner == "deepseek":
                envoy = OpenAI(
                    api_key=os.getenv("DEEPSEEK_KEY"),
                    max_retries=5,
                    base_url="https://api.deepseek.com",
                )
                spoken, influx, outflux = Conduit(breed, petition, [], envoy).relay()
            elif banner == "claude":
                spoken, influx, outflux = anthropic_relay(breed, petition)
            elif banner == "gemini":
                spoken, influx, outflux = gemini_relay(breed, petition)
            elif banner == "mistral":
                spoken, influx, outflux = mistral_relay(breed, petition)
            else:
                raise ValueError(f"Unknown model type: {banner}")

            ledger.tally(influx, outflux, breed)
            return spoken + TRAILER

        except Exception as mishap:
            print(f"Error in {banner.upper()} API call. Attempt {round_no + 1}: {mishap}")
            if round_no < attempts - 1:
                time.sleep(dwell)
            else:
                ledger.tally(0, 0, breed)
                raise RuntimeError(f"{banner.upper()} Classification failed") from mishap
