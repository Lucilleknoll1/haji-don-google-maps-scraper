import argparse
import csv
import json
import sys
from pathlib import Path


def load_entries(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if text.startswith("["):
        data = json.loads(text)
        return data if isinstance(data, list) else [data]

    entries = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def score_entry(entry):
    status = entry.get("business_status") or "unknown"
    claim = entry.get("claim_state") or "unknown"

    if status == "permanently_closed":
        return -100, "EXCLUDE"

    score = 0
    if claim == "unclaimed":
        score += 40
    elif claim == "unknown":
        # Validation sample: 10/10 unknown-claim listings showed the
        # "Claim this business" CTA in the Google Maps UI.
        score += 20
    if status == "temporarily_closed":
        score += 25
    if entry.get("phone"):
        score += 15
    if entry.get("web_site"):
        score += 10
    if (entry.get("review_count") or 0) >= 20:
        score += 10
    if (entry.get("review_rating") or 0) >= 4.0:
        score += 5

    tier = "A" if score >= 70 else "B" if score >= 50 else "C"
    return score, tier


def angle(entry):
    status = entry.get("business_status") or "unknown"
    claim = entry.get("claim_state") or "unknown"

    if status == "permanently_closed":
        return "Exclude: listing is permanently closed."
    if claim == "unclaimed" and status == "temporarily_closed":
        return "Urgent: unclaimed listing + temporarily closed; recovery + claim."
    if claim == "unclaimed":
        return "GBP claim + listing control; hours, photos, reviews are unmanaged."
    if claim == "unknown" and status != "permanently_closed":
        return "Likely unclaimed (verify): claim check + listing control."
    if status == "temporarily_closed":
        return "Reopening visibility: verify closure, fix hours, recovery campaign."
    if claim == "claimed":
        return "Listing optimization / local SEO; owner already controls the profile."
    return "Claim status unknown; verify listing ownership before outreach."


def claim_interpretation(entry):
    claim = entry.get("claim_state") or "unknown"

    if claim == "unclaimed":
        return "confirmed_unclaimed"
    if claim == "unknown":
        return "likely_unclaimed_verify"
    if claim == "conflict":
        return "conflict_verify"
    if claim == "claimed":
        return "claimed"

    return "unknown"


def verification_note(entry):
    status = entry.get("business_status") or "unknown"
    claim = entry.get("claim_state") or "unknown"

    notes = []
    if status == "temporarily_closed":
        notes.append("Call first: temporary label can be wrong or mean closed for the day.")
    if claim == "unclaimed":
        notes.append("Re-check claim link on Map before sending.")
    if claim == "unknown":
        notes.append("10/10 sampled unknown-claim listings were unclaimed in Google Maps UI; confirm the Claim this business CTA before sending.")
    if not notes:
        notes.append("Standard verification.")
    return " ".join(notes)


def dedupe_key(entry):
    return (
        entry.get("place_id")
        or entry.get("cid")
        or entry.get("data_id")
        or f"{entry.get('title', '')}|{entry.get('address', '')}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--include-closed", action="store_true")
    args = parser.parse_args()

    entries = load_entries(args.input)
    if not entries:
        print("No entries found.")
        return 1

    seen = set()
    rows = []

    for entry in entries:
        key = dedupe_key(entry)
        if key in seen:
            continue
        seen.add(key)

        score, tier = score_entry(entry)
        if tier == "EXCLUDE" and not args.include_closed:
            continue

        rows.append({
            "title": entry.get("title", ""),
            "tier": tier,
            "score": score,
            "business_status": entry.get("business_status", ""),
            "claim_state": entry.get("claim_state", ""),
            "claim_interpretation": claim_interpretation(entry),
            "claim_evidence": entry.get("claim_evidence", ""),
            "status_badge": entry.get("status_badge", ""),
            "category": entry.get("category", ""),
            "phone": entry.get("phone", ""),
            "website": entry.get("web_site", ""),
            "address": entry.get("address", ""),
            "review_count": entry.get("review_count", ""),
            "rating": entry.get("review_rating", ""),
            "place_id": entry.get("place_id", ""),
            "cid": entry.get("cid", ""),
            "link": entry.get("link", ""),
            "recommended_angle": angle(entry),
            "verification_note": verification_note(entry),
        })

    rows.sort(key=lambda row: (-row["score"], row["title"]))

    fieldnames = list(rows[0].keys()) if rows else [
        "title", "tier", "score", "business_status", "claim_state",
        "claim_evidence", "status_badge", "category", "phone", "website",
        "address", "review_count", "rating", "place_id", "cid", "link",
        "recommended_angle", "verification_note",
    ]

    with args.output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for row in rows:
        counts[row["tier"]] = counts.get(row["tier"], 0) + 1

    print(f"wrote {len(rows)} leads to {args.output}")
    print("tiers", counts)
    print("excluded_permanently_closed", len(entries) - len(rows) if not args.include_closed else 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
