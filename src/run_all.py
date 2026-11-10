import os, csv
from agent import analyze

folder = "data/sample_jds"
out = "results.csv"
header = ["file", "role_type", "fit_score", "matching_skills", "missing_skills"]
MIN_CHARS = 200

done = {}
if os.path.exists(out):
    with open(out, encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and row[0] != "file" and row[1] != "FAILED":
                done[row[0]] = row


def save():
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows([done[k] for k in sorted(done)])


for name in sorted(os.listdir(folder)):
    if not name.endswith(".txt") or name in done:
        continue
    with open(os.path.join(folder, name), encoding="utf-8") as f:
        jd = f.read()
    if len(jd.strip()) < MIN_CHARS:
        print(f"Skipping {name}: file is empty or too short")
        continue
    print(f"Running {name}...")
    result = analyze(jd)
    if result is None:
        print("Stopping: no model available right now. Run again later.")
        break
    done[name] = [
        name,
        result.get("role_type", ""),
        result.get("fit_score", ""),
        ", ".join(result.get("matching_skills", [])),
        ", ".join(result.get("missing_skills", [])),
    ]
    save()

save()
print("Done. See results.csv")