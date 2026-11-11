# JD Analyzer Agent

An LLM agent in Python that reads a job description, calls a tool to fetch my skills, and returns structured JSON: role type, required skills, matching skills, missing skills and a fit score. It runs from the command line or from a small Streamlit web app.

## Problem
Checking whether a job description fits my skills by hand is slow and inconsistent.

## Solution
The agent sends the job description to an LLM with a system prompt. The model decides on its own to call a `get_my_skills` tool, compares the result with the job description, and returns JSON. Every run is logged to a JSONL file so the reasoning steps can be reviewed afterwards.

## Tech stack
Python, Google Gemini API (`google-genai`), Streamlit, python-dotenv, JSON

## Project structure
- `app.py`: Streamlit web app (paste a job description, see matches and gaps)
- `src/agent.py`: LLM call, tool calling, input validation, retry, timeout and model fallback
- `src/tools.py`: the `get_my_skills` tool
- `src/logger.py`: saves every run to `logs/logs.jsonl`
- `src/main.py`: analyze one job description from a file
- `src/run_all.py`: analyze every file in `data/sample_jds` and write `results.csv`
- `prompts/system_prompt.md`: the model's instructions
- `data/my_skills.json`: the candidate's skills

## How to run
1. Create and activate a virtual environment, then `pip install -r requirements.txt`
2. Add your key to a `.env` file: `GEMINI_API_KEY=your-key`
3. Web app: `streamlit run app.py`
4. One job from the terminal: `python src/main.py data/sample_jds/jd_01.txt`
5. All jobs: `python src/run_all.py` (results go to `results.csv`, full traces to `logs/logs.jsonl`)

## Example output
```json
{
  "role_type": "AI Engineering Intern",
  "required_skills": ["Python", "REST APIs", "LLM APIs", "Prompt Engineering"],
  "matching_skills": ["Python", "REST APIs", "JSON", "SQL", "Git"],
  "missing_skills": ["LLM APIs", "LLM Agent SDKs", "Prompt Engineering", "MCP"],
  "fit_score": 6
}
```

## Results
Tested on 3 real job descriptions (AI Engineering Intern, QA Automation Engineer, Software Engineer). In each, every matching skill was on my skills list, so no skills were invented. More tests are in progress.

## Failures and fixes
- **Answers on empty input:** the model returned confident results for empty job description files. Fix: the batch script skips files under 200 characters, and the agent rejects empty input.
- **Wrong "missing" skill:** for the QA job, the model listed Test Automation as missing even though my skills included Selenium and pytest. Cause: my skills file was too thin. Fix: expanded the skills file to match my real experience and re-ran. Test Automation became a match and the score moved from 8 to 8.5.
- **Output depends on the skills file:** the model flags topics such as OOP and Data Structures as missing when they are not listed, so the result is only as accurate as the skills data.
- **Unstable output:** the same job description gave different fit scores (5 and 6) and slightly different role types across runs. The score is a rough signal, not a measurement.
- **Quota and availability errors:** the free-tier limit (429), a retired model (404) and busy servers (503) caused failures. Fix: the agent retries with a delay on 503, moves to a fallback model on quota or model errors, and stops cleanly if none is available.
- **App froze with no error:** the web app waited indefinitely when a model did not respond. Fix: added a 60-second request timeout and put the more reliable model first.

## Next improvements
- Test on 10 or more job descriptions
- Add an evaluation set with expected answers
- Add LLM observability tracing (e.g. Langfuse)