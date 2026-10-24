import csv
import json
import os
import subprocess

urls = [
    row["url"]
    for row in csv.DictReader(open("/content/verify_sample.csv", encoding="utf-8"))
    if row["group"] == "unknown_claim"
]

with open("/content/q_unknown.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(urls) + "\n")

cmd = [
    "/content/gmaps-scraper",
    "-input", "/content/q_unknown.txt",
    "-geo", "40.7128,-74.0060",
    "-radius", "50000",
    "-zoom", "15",
    "-lang", "en",
    "-depth", "1",
    "-c", "2",
    "-json",
    "-results", "/content/claim_fix.json",
    "-exit-on-inactivity", "2m",
]

r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=600)
print("RC", r.returncode)
print("STDERR", r.stderr[-1500:])

if os.path.exists("/content/claim_fix.json"):
    print("SIZE", os.path.getsize("/content/claim_fix.json"))
    for line in open("/content/claim_fix.json", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        print({
            "title": e.get("title"),
            "status": e.get("business_status"),
            "claim": e.get("claim_state"),
            "evidence": e.get("claim_evidence"),
            "claim_url": (e.get("claim_url") or "")[:60],
        })
