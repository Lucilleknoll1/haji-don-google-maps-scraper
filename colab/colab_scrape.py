import json
import os
import subprocess

queries = "/content/queries.txt"
out = "/content/out.json"

with open(queries, "w", encoding="utf-8") as f:
    f.write("Sears 87 Mall Walk Yonkers\n")

cmd = [
    "/content/gmaps-scraper",
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
    r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=480)
    print("RC", r.returncode)
    print("STDOUT", r.stdout[-6000:])
    print("STDERR", r.stderr[-6000:])
except subprocess.TimeoutExpired as e:
    print("TIMEOUT")
    print((e.stdout or b"")[-4000:])
    print((e.stderr or b"")[-4000:])

if os.path.exists(out):
    print("OUT SIZE", os.path.getsize(out))
    with open(out, encoding="utf-8") as f:
        text = f.read()
    print("HEAD", text[:500])
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data = [data]
        print("COUNT", len(data))
        for e in data[:5]:
            print({
                "title": e.get("title"),
                "status": e.get("status"),
                "business_status": e.get("business_status"),
                "status_badge": e.get("status_badge"),
                "highlight": e.get("highlight"),
                "hours_summary": e.get("hours_summary"),
                "claim_state": e.get("claim_state"),
                "claim_url": (e.get("claim_url") or "")[:80],
                "claim_evidence": e.get("claim_evidence"),
                "owner_gaia_id": e.get("owner_gaia_id"),
            })
    except Exception as exc:
        print("PARSE ERR", exc)
