import json

def get_my_skills() -> list:
    """Returns the candidate's skills as a list of strings."""
    with open("data/my_skills.json", encoding="utf-8") as f:
        return json.load(f)