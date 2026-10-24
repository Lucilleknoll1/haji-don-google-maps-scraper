import json
import os
import subprocess

queries = "/content/q_fast_dream.txt"
out = "/content/fast_dream.json"

with open(queries, "w", encoding="utf-8") as f:
    f.write("Dream Coffee Ilion Greece\n")

cmd = [
    "/content/gmaps-scraper",
    "-fast-mode",
    "-input", queries,
    "-geo", "38.0272632,23.7100223",
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
print("STDERR", r.stderr[-1500:])

if os.path.exists(out):
    print("SIZE", os.path.getsize(out))
    data = json.load(open(out, encoding="utf-8"))
    print("TYPE", type(data).__name__, "N", len(data) if isinstance(data, list) else "?")
    rows = data if isinstance(data, list) else [data]
    for e in rows:
        print({
            "title": e.get("title"),
            "status": e.get("business_status"),
            "claim": e.get("claim_state"),
            "evidence": e.get("claim_evidence"),
            "claim_url": (e.get("claim_url") or "")[:90],
            "highlight": e.get("highlight"),
        })
