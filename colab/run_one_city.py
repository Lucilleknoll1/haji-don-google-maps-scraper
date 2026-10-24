import json
import os
import subprocess

CITIES = {
    "yonkers": {
        "geo": "40.9312,-73.8988",
        "queries": [
            "restaurants in Yonkers NY",
            "coffee shops in Yonkers NY",
            "hair salons in Yonkers NY",
            "auto repair in Yonkers NY",
            "gyms in Yonkers NY",
        ],
    },
    "brooklyn": {
        "geo": "40.6782,-73.9442",
        "queries": [
            "restaurants in Brooklyn NY",
            "coffee shops in Brooklyn NY",
            "nail salons in Brooklyn NY",
            "dentists in Brooklyn NY",
            "gyms in Brooklyn NY",
        ],
    },
    "jerseycity": {
        "geo": "40.7178,-74.0431",
        "queries": [
            "restaurants in Jersey City NJ",
            "barbershops in Jersey City NJ",
            "laundromats in Jersey City NJ",
            "auto repair in Jersey City NJ",
            "real estate agencies in Jersey City NJ",
        ],
    },
    "deadbrands": {
        "geo": "40.7128,-74.0060",
        "radius": "50000",
        "queries": [
            "Sears Yonkers NY",
            "Sears Brooklyn NY",
            "Sears Jersey City NJ",
            "RadioShack Brooklyn NY",
            "Blockbuster Brooklyn NY",
            "Toys R Us Brooklyn NY",
            "Bed Bath & Beyond Brooklyn NY",
            "Payless ShoeSource Brooklyn NY",
        ],
    },
}

city = os.environ["CITY"]
cfg = CITIES[city]
queries_path = f"/content/q2_{city}.txt"
out = f"/content/val2_{city}.json"

with open(queries_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cfg["queries"]) + "\n")

cmd = [
    "/content/gmaps-scraper",
    "-input", queries_path,
    "-geo", cfg["geo"],
    "-zoom", "15",
    "-lang", "en",
    "-depth", "1",
    "-c", "2",
    "-json",
    "-results", out,
    "-exit-on-inactivity", "2m",
]
if cfg.get("radius"):
    cmd[cmd.index("-zoom"):cmd.index("-zoom")] = ["-radius", cfg["radius"]]

r = subprocess.run(cmd, cwd="/content", capture_output=True, text=True, timeout=700)
print("RC", r.returncode)
print("STDERR", r.stderr[-2000:])

if os.path.exists(out):
    print("SIZE", os.path.getsize(out))
    count = 0
    statuses = {}
    claims = {}
    for line in open(out, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        count += 1
        statuses[e.get("business_status")] = statuses.get(e.get("business_status"), 0) + 1
        claims[e.get("claim_state")] = claims.get(e.get("claim_state"), 0) + 1
    print("COUNT", count)
    print("STATUS", statuses)
    print("CLAIM", claims)
