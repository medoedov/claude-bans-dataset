"""Join the reviewed Russian material without counting reports as independent people.

Local: python integrate.py
Published copy: python integrate.py --base ../../v2 --pool ../2026-11-06-ru-focus
Inputs beside this script are public, sanitized research artifacts.
"""
import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def index_unique(rows, key):
    indexed = {}
    for row in rows:
        value = row[key]
        if value in indexed:
            raise ValueError(f"Duplicate {key}: {value}")
        indexed[value] = row
    return indexed


def integrate(cases, membership, details, events, sources, new, dashi, audit,
              followups, author, decisions, extra_corrections):
    base = index_unique(copy.deepcopy(cases), "case_id")
    members = index_unique(membership, "case_id")
    if set(members) - set(base):
        raise ValueError("Candidate membership refers to unknown base cases")
    records = {
        cid: {"case": base[cid], "inclusion": {
            "cohort": "unreviewed", "basis": members[cid]["reasons"],
            "reason": "Selection flags are not confirmation of citizenship."},
            "unit": "unreviewed_case_row", "details": [], "events": [],
            "sources": [], "observations": [], "corrections": []}
        for cid in members
    }
    for name, rows in (("details", details), ("events", events), ("sources", sources)):
        for row in rows:
            cid = row["case_id"]
            if cid not in base:
                raise ValueError(f"Unknown case in {name}: {cid}")
            if cid in records:
                records[cid][name].append(copy.deepcopy(row))

    materials = index_unique(copy.deepcopy(new + dashi["records"]), "candidate_id")
    for episode in audit["episodes"]:
        for cid in episode.get("case_ids", []):
            if cid not in records:
                raise ValueError(f"Audit case missing from candidate pool: {cid}")
            records[cid]["observations"].append(copy.deepcopy(episode))
    review = index_unique(decisions, "record_id")
    allowed = set(records) | set(materials) | {"audit:" + e["audit_id"] for e in audit["episodes"]}
    allowed.add("ru-prevention-001")
    for key in review:
        if key.startswith("series:") and set(key.split(":")[1:]) <= set(records):
            allowed.add(key)
    if set(review) - allowed:
        raise ValueError(f"Unknown review records: {set(review) - allowed}")
    for key, decision in review.items():
        for cid in decision.get("existing_case_ids", []):
            if cid not in records:
                raise ValueError(f"Unknown linked case: {cid}")
        if key in records:
            records[key]["inclusion"] = copy.deepcopy(decision)
            if decision.get("unit"):
                records[key]["unit"] = decision["unit"]
        if key in materials:
            materials[key]["review"] = copy.deepcopy(decision)
        if key.startswith(("audit:", "series:")):
            for cid in decision.get("existing_case_ids", []):
                records[cid]["inclusion"] = copy.deepcopy(decision)
        # Candidate-to-base links stay explicit; an unresolved possible duplicate
        # must not overwrite an account's latest status.
    if set(materials) - set(review):
        raise ValueError("Every new material needs an inclusion/dedup decision")

    corrections = copy.deepcopy(audit["corrections"] + extra_corrections)
    for correction in corrections:
        cid = correction["case_id"]
        record = records[cid]
        field = correction["field"]
        if field in record["case"]:
            old = record["case"][field]
            if "published_value" in correction and str(old) != str(correction["published_value"]):
                raise ValueError(f"Correction precondition mismatch: {cid}.{field}")
            correction["previous_value"] = old
            record["case"][field] = correction["audited_value"]
        elif field == "unit_of_observation":
            record["unit"] = "owner_aggregate"
        elif field == "details.document_country":
            previous = []
            for detail in record["details"]:
                parsed = json.loads(detail["details_json"])
                if "document_country" in parsed:
                    previous.append(parsed["document_country"])
                    parsed["document_country"] = correction["audited_value"]
                    detail["details_json"] = json.dumps(parsed, ensure_ascii=False, sort_keys=True)
            correction["previous_detail_values"] = previous
        # Non-case fields are explicit audit annotations, not invented CSV columns.
        record["corrections"].append(correction)

    for update in followups:
        record = records[update["case_id"]]
        record["observations"].append(copy.deepcopy(update))
        if update["event"] == "appeal_rejected":
            record["case"]["appeal"] = "rejected"
        date = update.get("observed_at")
        if date and date > record["case"].get("last_observed_at", ""):
            record["case"]["last_observed_at"] = date
    record = records[author["case_id"]]
    record["observations"].append(copy.deepcopy(author))
    for field in ("outcome", "appeal"):
        record["case"][field] = author[field]
    if author["reported_on"] > record["case"].get("last_observed_at", ""):
        record["case"]["last_observed_at"] = author["reported_on"]

    summary = {
        "base_case_rows": len(base), "preserved_candidate_rows": len(records),
        "new_material_rows": len(materials), "audited_series": len(audit["episodes"]),
        "base_field_corrections": sum("previous_value" in c for c in corrections),
        "correction_annotations": len(corrections),
        "explicit_followups": len(followups) + 1,
        "review_decisions": len(review),
        "base_inclusion": dict(Counter(r["inclusion"]["cohort"] for r in records.values())),
        "new_material_inclusion": dict(Counter(m["review"]["cohort"] for m in materials.values())),
        "interpretation": "Record inventory only. No total of new independent accounts, people or ban probability."
    }
    return {"schema_version": 1, "as_of": "2026-11-07", "summary": summary,
            "base_records": list(records.values()), "new_materials": list(materials.values()),
            "series_audit": audit["episodes"], "review_decisions": list(review.values()),
            "dedup_decisions": audit["dedup_decisions"], "followups": followups}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=ROOT.parent / "release" / "v2")
    parser.add_argument("--pool", type=Path, default=ROOT)
    args = parser.parse_args()
    paths = {name: args.base / (name + ".csv") for name in ("cases", "details", "events", "sources")}
    paths["membership"] = args.pool / "membership.csv"
    names = ["new-evidence", "dashi-candidates", "prevention-audit", "followups",
             "author-followup-public", "inclusion-new-review", "inclusion-dashi-review", "integration-overrides"]
    paths.update({name: ROOT / (name + ".json") for name in names})
    data = {name: read_json(path) for name, path in paths.items() if path.suffix == ".json"}
    decisions = (data["inclusion-new-review"]["decisions"] + data["inclusion-dashi-review"]["decisions"]
                 + data["integration-overrides"]["decisions"])
    result = integrate(*(read_csv(paths[n]) for n in ("cases", "membership", "details", "events", "sources")),
                       data["new-evidence"], data["dashi-candidates"], data["prevention-audit"],
                       data["followups"], data["author-followup-public"], decisions,
                       data["integration-overrides"]["corrections"])
    # Git changes CRLF to LF. Hash decoded content so a fresh clone reproduces
    # the manifest on both Windows and Unix without changing the source files.
    result["input_hash_encoding"] = "UTF-8 without BOM, universal newlines normalized to LF"
    result["input_sha256"] = {
        name: hashlib.sha256(path.read_text(encoding="utf-8-sig").encode("utf-8")).hexdigest()
        for name, path in paths.items()
    }
    for filename, value in (("integrated.json", result), ("integration-summary.json", result["summary"])):
        (ROOT / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
