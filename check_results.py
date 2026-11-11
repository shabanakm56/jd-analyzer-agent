import csv, json

with open("data/my_skills.json", encoding="utf-8") as f:
    my_skills = {s.lower() for s in json.load(f)}

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Jobs analyzed: {len(rows)}\n")
bad = 0
for row in rows:
    matches = [s.strip() for s in row["matching_skills"].split(",") if s.strip()]
    invented = [s for s in matches if s.lower() not in my_skills]
    status = "OK" if not invented else f"CHECK: {invented}"
    if invented:
        bad += 1
    print(f"{row['file']:12} {row['role_type']:35} score {row['fit_score']:5}  {status}")

print(f"\n{len(rows) - bad} of {len(rows)} had every matching skill on my skills list.")
