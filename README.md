# JD Analyzer Agent

An LLM agent in Python that compares a job description with my skills. It returns structured JSON with the role type, required skills, matching skills, missing skills and a fit score, and it logs every run for review. It runs from a Streamlit web app or from the command line.

## Why I built it
Checking by hand whether a job fits my skills is slow and inconsistent. This agent does it in seconds and records exactly how it reached each answer.

## How it works
1. A job description is pasted into the app (or read from a file).
2. It is sent to the Gemini model with a system prompt.
3. The model decides on its own to call the `get_my_skills` tool, which reads my skills from `data/my_skills.json`.
4. The model compares the two and returns JSON.
5. The app shows matching skills, missing skills and the fit score, and every step is saved to `logs/logs.jsonl`.

## Features
- Tool calling: the model chooses when to fetch my skills
- Structured JSON output with parsing and validation
- Step-by-step run logs (JSONL) for reviewing the agent's reasoning
- Reliability handling: empty-input checks, retry with backoff on busy servers, request timeout, and fallback model on quota errors
- Streamlit web app that runs locally, plus a batch mode that tests many job descriptions at once
- Validation script that checks every matching skill against my skills list

## Tech stack
Python, Google Gemini API (`google-genai`), Streamlit, python-dotenv, JSON

## Project structure
- `app.py`: Streamlit web app
- `src/agent.py`: LLM call, tool calling, validation, retry, timeout and model fallback
- `src/tools.py`: the `get_my_skills` tool
- `src/logger.py`: writes every run to `logs/logs.jsonl`
- `src/main.py`: analyze one job description from a file
- `src/run_all.py`: analyze every file in `data/sample_jds` and write `results.csv`
- `check_results.py`: checks that every matching skill in `results.csv` comes from my skills list
- `prompts/system_prompt.md`: the model's instructions
- `data/my_skills.json`: the skills the agent compares against

## Getting started
1. Create a virtual environment and install dependencies: `pip install -r requirements.txt`
2. Add your Gemini API key to a `.env` file: `GEMINI_API_KEY=your-key`
3. Edit `data/my_skills.json` with your own skills
4. Run the web app: `streamlit run app.py`
5. Or run from the terminal: `python src/main.py data/sample_jds/jd_01.txt`
6. Or test many files: `python src/run_all.py`, then validate with `python check_results.py`

The app runs on localhost only (see `.streamlit/config.toml`).

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
Tested on 6 real job descriptions through the batch script. In all 6, every matching skill was on my skills list (checked with `check_results.py`), so no skills were invented.

| Role | Fit score |
|------|-----------|
| AI Engineering Intern | 6 |
| QA Automation Engineer | 8.5 |
| Web Developer | 5 |
| Artificial Intelligence Engineer | 2 |
| Software Engineer | 8 |
| Technical Support Executive | 1 |

The scores separate well-matched roles from poorly matched ones, but the same job can score differently between runs, so the score is a rough signal. 4 more job descriptions will be run when the free API quota resets.

## Failures and fixes
- **Answers on empty input:** the model returned confident results for empty files. Fix: input validation in the agent, and the batch script skips files under 200 characters.
- **Wrong "missing" skill:** the model listed Test Automation as missing although my skills included Selenium and pytest. Cause: my skills file was too thin. Fix: expanded the skills data and re-ran; the score moved from 8 to 8.5.
- **Accuracy depends on the skills data:** topics not listed (for example OOP or Data Structures) are reported as missing, so the output is only as good as `my_skills.json`.
- **Unstable output:** the same job description gave different scores (5 and 6) across runs. Setting a low temperature reduces this, but the score is still a rough signal.
- **Quota and availability errors:** free-tier limits (429), a retired model (404), busy servers (503) and timeouts (504) caused failures. Fix: backoff on 503, fallback model on quota errors, and a clean stop that lets the batch script resume later.
- **App froze with no error:** the web app waited indefinitely when a model did not respond. Fix: added a 60-second timeout and put the more reliable model first.

## Next improvements
- Run the remaining job descriptions and extend the test set
- Add an evaluation set with expected answers
- Add LLM observability tracing (for example Langfuse)