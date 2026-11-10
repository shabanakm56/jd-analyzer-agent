import json, os
from datetime import datetime


def log_step(kind, data):
    os.makedirs("logs", exist_ok=True)
    entry = {"time": datetime.now().isoformat(), "type": kind, "data": data}
    with open("logs/logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")