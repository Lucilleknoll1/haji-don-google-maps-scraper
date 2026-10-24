import json
import os
import subprocess

queries = "/content/q_fast.txt"
out = "/content/fast_yonkers.json"

with open(queries, "w", encoding="utf-8") as f:
    f.write("coffee shops in Yonkers NY\n")

cmd = [
    "/content/gmaps-scraper",
    "-fast-mode",
    "-input", queries,
    "-geo", "40.9312,-73.8988",
    "-zoom", "15",
    "-lang", "en",
    "-depth", "1",
    "-c", "1",
    "-json",
    "-results", out,
    "-exit-on-inactivity", "2m",
]

r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=420)
print("RC", r.returncode)
print("STDERR", r.stderr[-2500:])

if os.path.exists(out):
    print("SIZE", os.path.getsize(out))
    count = 0
    for line in open(out, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        count += 1
        print({
            "title": e.get("title"),
            "status": e.get("business_status"),
            "claim": e.get("claim_state"),
            "evidence": e.get("claim_evidence"),
        })
    print("COUNT", count)
