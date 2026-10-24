import json
import os
import subprocess

queries = "/content/queries_unclaimed.txt"
out = "/content/unclaimed.json"

with open(queries, "w", encoding="utf-8") as f:
    f.write("Dream Coffee Ilion Greece\n")

cmd = [
    "/content/gmaps-scraper",
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

try:
    r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=420)
    print("RC", r.returncode)
    print("STDERR", r.stderr[-2500:])
except subprocess.TimeoutExpired as e:
    print("TIMEOUT")
    print((e.stderr or b"")[-2500:])

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
            "highlight": e.get("highlight"),
            "claim_state": e.get("claim_state"),
            "claim_url": (e.get("claim_url") or "")[:80],
            "claim_evidence": e.get("claim_evidence"),
            "owner_gaia_id": e.get("owner_gaia_id"),
        })
