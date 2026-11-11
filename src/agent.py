import os
import json
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import get_my_skills
from logger import log_step


# Project paths
ROOT = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

# Try the latest model first, then the fallback
MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]

client = (
    genai.Client(api_key=API_KEY, http_options=types.HttpOptions(timeout=60000))
    if API_KEY
    else None
)

def load_prompt():
    """Load the system prompt."""
    prompt_path = ROOT / "prompts" / "system_prompt.md"

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


def clean_json(text):
    """Remove Markdown code fences from model output."""
    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


def analyze(jd_text):
    """Analyze a job description using Gemini."""

    if not API_KEY or client is None:
        print("ERROR: GEMINI_API_KEY is missing from .env")
        return None

    if not jd_text or not jd_text.strip():
        print("ERROR: Job description is empty.")
        return None

    try:
        system_prompt = load_prompt()
    except Exception as e:
        print(f"ERROR loading system prompt: {e}")
        return None

    for model in MODELS:

        print(f"\nTrying Gemini model: {model}")

        for attempt in range(3):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=jd_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        tools=[get_my_skills],
                        temperature=0.2,
                    ),
                )

                response_text = response.text

                if not response_text:
                    print("ERROR: Gemini returned an empty response.")
                    break

                # Log function-calling history
                history = (
                    getattr(
                        response,
                        "automatic_function_calling_history",
                        None,
                    )
                    or []
                )

                print(f"SUCCESS: Model used: {model}")
                print(f"Function calls: {len(history)}")

                try:
                    log_step(
                        "run",
                        {
                            "model": model,
                            "history": [
                                h.model_dump(
                                    mode="json",
                                    exclude_none=True,
                                )
                                for h in history
                            ],
                            "final_text": response_text,
                        },
                    )
                except Exception as log_error:
                    print(f"Logging warning: {log_error}")

                # Convert response into JSON
                cleaned_text = clean_json(response_text)

                try:
                    result = json.loads(cleaned_text)

                    if not isinstance(result, dict):
                        print("ERROR: Expected a JSON object.")
                        return None

                    print("Analysis completed successfully!")
                    return result

                except json.JSONDecodeError as json_error:
                    print(f"Invalid JSON response: {json_error}")
                    print(response_text[:1000])
                    return None

            except Exception as e:

                message = str(e)
                print(
                    f"{model} attempt {attempt + 1} failed: "
                    f"{message[:700]}"
                )

                # Quota exceeded: try the next model without
                # repeatedly sending requests to this model.
                if "429" in message or "RESOURCE_EXHAUSTED" in message:
                    print("Quota/rate limit reached. Trying fallback model.")
                    break

                # Model unavailable: retry with increasing delay.
                if "503" in message or "UNAVAILABLE" in message:
                    if attempt < 2:
                        wait_time = 5 * (2 ** attempt)
                        print(f"Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    continue

                # Other errors: try the next model.
                break

    print("\nAll Gemini model attempts failed.")
    print("Check your API quota and model availability.")

    return None
