import glob
import subprocess

paths = sorted(glob.glob("/content/val_*.json")) + sorted(glob.glob("/content/val2_*.json"))

with open("/content/validation_all.jsonl", "w", encoding="utf-8") as out:
    for path in paths:
        text = open(path, encoding="utf-8").read().strip()
        out.write(text + "\n")

for label, src, dst in [
    ("validation", "/content/validation_all.jsonl", "/content/leads_validation.csv"),
    ("unknown_sample", "/content/claim_fix.json", "/content/leads_unknown_sample.csv"),
]:
    r = subprocess.run(
        ["python3", "/content/outreach_leads.py", src, dst],
        capture_output=True,
        text=True,
    )
    print("==", label, "RC", r.returncode)
    print(r.stdout)
    print(r.stderr)
