import json
import os
import subprocess

queries = "/content/queries.txt"
out = "/content/fast.json"

with open(queries, "w", encoding="utf-8") as f:
    f.write("Sears 87 Mall Walk Yonkers\n")

cmd = [
    "/content/gmaps-scraper",
    "-fast-mode",
    "-input", queries,
    "-geo", "40.9281543,-73.8512761",
    "-zoom", "15",
    "-lang", "en",
    "-depth", "1",
    "-c", "1",
    "-json",
    "-results", out,
    "-exit-on-inactivity", "2m",
]

try:
    r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=420)
    print("RC", r.returncode)
    print("STDOUT", r.stdout[-3000:])
    print("STDERR", r.stderr[-3000:])
except subprocess.TimeoutExpired as e:
    print("TIMEOUT")
    print((e.stderr or b"")[-3000:])

if os.path.exists(out):
    print("OUT SIZE", os.path.getsize(out))
    for line in open(out, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        print({
            "title": e.get("title"),
            "status": e.get("status"),
            "business_status": e.get("business_status"),
            "status_badge": e.get("status_badge"),
            "highlight": e.get("highlight"),
            "claim_state": e.get("claim_state"),
            "claim_url": (e.get("claim_url") or "")[:70],
            "claim_evidence": e.get("claim_evidence"),
        })
