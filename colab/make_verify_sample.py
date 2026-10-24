import csv
import glob
import json
import random

files = sorted(glob.glob("/content/val_*.json")) + sorted(glob.glob("/content/val2_*.json"))

entries = []
seen = set()

for path in files:
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        key = e.get("place_id") or e.get("cid") or e.get("link")
        if key in seen or not e.get("link"):
            continue
        seen.add(key)
        entries.append(e)

closed = [e for e in entries if e.get("business_status") == "permanently_closed"]
unknown_claim = [e for e in entries if e.get("claim_state") == "unknown"]
claimed = [e for e in entries if e.get("claim_state") == "claimed"]

rng = random.Random(42)
rows = []
rows += [("closed", e["link"]) for e in rng.sample(closed, min(10, len(closed)))]
rows += [("unknown_claim", e["link"]) for e in rng.sample(unknown_claim, min(10, len(unknown_claim)))]
rows += [("claimed", e["link"]) for e in rng.sample(claimed, min(3, len(claimed)))]
rows.append((
    "known_unclaimed_dream",
    "https://www.google.com/maps/place/Dream+Coffee/@38.0272632,23.7100223,15z/data=!4m6!3m5!1s0x14a1a32f316b15a1:0x169c54b46dcc3a93!8m2!3d38.0331931!4d23.7094475!16s%2Fg%2F11ghrv6fdh?hl=en",
))

with open("/content/verify_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["group", "url"])
    writer.writerows(rows)

print("closed", len(closed), "unknown_claim", len(unknown_claim), "claimed", len(claimed))
print("sample_rows", len(rows))
