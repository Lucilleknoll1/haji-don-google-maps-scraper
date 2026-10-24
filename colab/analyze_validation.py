import csv
import glob
import json
import os
from collections import Counter

files = sorted(glob.glob("/content/val_*.json")) + sorted(glob.glob("/content/val2_*.json"))
print("files", files)

entries = []
seen = set()

for path in files:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            key = e.get("place_id") or e.get("cid") or e.get("link") or f"{e.get('title')}|{e.get('address')}"
            if key in seen:
                continue
            seen.add(key)
            e["_source"] = os.path.basename(path)
            entries.append(e)

print("total_unique", len(entries))
print("business_status", Counter(e.get("business_status") or "missing" for e in entries))
print("claim_state", Counter(e.get("claim_state") or "missing" for e in entries))
print("claim_evidence", Counter(e.get("claim_evidence") or "none" for e in entries))

flag_status = [
    e for e in entries
    if (e.get("business_status") or "unknown") != "unknown"
]
flag_claim = [
    e for e in entries
    if (e.get("claim_state") or "unknown") in ("unclaimed", "conflict")
]

print("flagged_status", len(flag_status))
print("flagged_claim", len(flag_claim))

for e in flag_status:
    print("STATUS", {
        "title": e.get("title"),
        "status": e.get("business_status"),
        "badge": e.get("status_badge"),
        "highlight": e.get("highlight"),
        "claim": e.get("claim_state"),
        "link": e.get("link"),
    })

for e in flag_claim:
    print("CLAIM", {
        "title": e.get("title"),
        "claim": e.get("claim_state"),
        "evidence": e.get("claim_evidence"),
        "status": e.get("business_status"),
        "link": e.get("link"),
    })

rows = []
for e in entries:
    if e in flag_status or e in flag_claim:
        rows.append(e)

with open("/content/flagged.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "title", "business_status", "status_badge", "claim_state",
        "claim_evidence", "phone", "website", "address", "rating",
        "review_count", "link",
    ])
    for e in rows:
        writer.writerow([
            e.get("title", ""),
            e.get("business_status", ""),
            e.get("status_badge", ""),
            e.get("claim_state", ""),
            e.get("claim_evidence", ""),
            e.get("phone", ""),
            e.get("web_site", ""),
            e.get("address", ""),
            e.get("review_rating", ""),
            e.get("review_count", ""),
            e.get("link", ""),
        ])

print("flagged_csv_rows", len(rows))
