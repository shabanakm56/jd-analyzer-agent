import os, json, time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import get_my_skills
from logger import log_step

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]


def load_prompt():
    with open("prompts/system_prompt.md", encoding="utf-8") as f:
        return f.read()


def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def analyze(jd_text):
    system_prompt = load_prompt()
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=jd_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        tools=[get_my_skills],
                    ),
                )
                history = getattr(response, "automatic_function_calling_history", None) or []
                print(f"Model used: {model} | history items: {len(history)}")
                log_step("run", {
                    "model": model,
                    "history": [h.model_dump(mode="json", exclude_none=True) for h in history],
                    "final_text": response.text,
                })
                text = clean_json(response.text)
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print("The model did not return valid JSON:")
                    print(response.text)
                    return None
            except Exception as e:
                message = str(e)
                print(f"{model} attempt {attempt + 1} failed: {message[:100]}")
                if "429" in message or "404" in message:
                    break  # quota or model problem: go to the next model now
                time.sleep(5)
    return None