# JD Analyzer Agent

An LLM agent in Python that reads a job description, calls a tool to fetch my skills, and returns structured JSON: role type, required skills, matching skills, missing skills and a fit score.

## Problem
Checking whether a job description fits my skills by hand is slow and inconsistent.

## Solution
The agent sends the job description to an LLM with a system prompt. The model decides on its own to call a `get_my_skills` tool, compares the result with the job description, and returns JSON. Every step is logged to a JSONL file.

## Tech stack
Python, Google Gemini API (`google-genai`), python-dotenv, JSON

## Project structure
- `src/agent.py`: LLM call, tool calling, retry and model fallback
- `src/tools.py`: the `get_my_skills` tool
- `src/logger.py`: saves every run to `logs/logs.jsonl`
- `src/main.py`: analyze one job description
- `src/run_all.py`: analyze every file in `data/sample_jds` and write `results.csv`
- `prompts/system_prompt.md`: the model's instructions
- `data/my_skills.json`: the candidate's skills

## How to run
1. Create and activate a virtual environment, then `pip install -r requirements.txt`
2. Add your key to a `.env` file: `GEMINI_API_KEY=your-key`
3. Run one job: `python src/main.py data/sample_jds/jd_01.txt`
4. Run all jobs: `python src/run_all.py`

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
Tested so far on 2 real job descriptions (AI Engineering Intern, QA Automation Engineer). More tests in progress.

## Failures and fixes
- **Answers on empty input:** the model returned confident results for empty job description files. Fix: the batch script now skips files under 200 characters.
- **Wrong "missing" skill:** for the QA job, the model listed Test Automation as missing even though my skills included Selenium and pytest. Cause: my skills file was too thin. Fix: expanded the skills file to match my real experience, then re-ran. Test Automation became a match and the score moved from 8 to 8.5.
- **Unstable output:** the same job description gave different fit scores (5 and 6) and slightly different role types across runs. Treat the score as a rough signal.
- **Quota and availability errors:** the free tier limit (429), a retired model (404) and busy servers (503) caused failures. Fix: the agent falls back to a second model and moves on quickly after a quota or model error.

## Next improvements
- Test on 10 or more job descriptions
- Add an evaluation set with expected answers
- Add LLM observability tracing (e.g. Langfuse)