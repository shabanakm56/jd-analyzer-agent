import sys, json
from agent import analyze

with open(sys.argv[1], encoding="utf-8") as f:
    jd_text = f.read()

result = analyze(jd_text)
print(json.dumps(result, indent=2))
