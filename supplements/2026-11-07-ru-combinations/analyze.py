"""Inventory and joint-setup tables. Never infer survival from an active label."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HORIZONS = {"insufficient", "worked_through_horizon", "ban_by_horizon"}


def prepare(data):
    rows = [{**data["defaults"], **row} for row in data["records"]]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate record ID")
    for r in rows:
        if r["physical_location"] not in {"RU", "abroad", "unknown"}:
            raise ValueError(f"Invalid location: {r['id']}")
        for h in (7, 30):
            if r[f"horizon_{h}"] not in HORIZONS:
                raise ValueError(f"Invalid horizon: {r['id']}")
        if not (r.get("urls") or r.get("refs")):
            raise ValueError(f"No source locator: {r['id']}")
        r["both_described"] = r["payment"] != "unknown" and r["network"] != "unknown"
        # Described does not mean a precise provider/type, or a dated joint episode.
        r["eligible_episode"] = r["kind"] == "episode" and r["evidence"] == "opened"
    return rows


def inventory(rows):
    episodes = [r for r in rows if r["eligible_episode"]]
    return {
        "records": len(rows),
        "episode_records": len(episodes),
        "account_keys": len({r["account"] for r in episodes}),
        "owner_keys": len({r["owner"] for r in episodes}),
        "by_kind": dict(Counter(r["kind"] for r in rows)),
        "by_source": dict(Counter(r["source"] for r in rows)),
        "by_newness": dict(Counter(r["newness"] for r in rows)),
        "episodes_by_location": dict(Counter(r["physical_location"] for r in episodes)),
        "both_described_by_location": dict(Counter(r["physical_location"] for r in episodes if r["both_described"])),
        "caution": "Keys are research identities, not verified unique people. Re-audits and linked episodes are not new independent accounts.",
    }


def joint_tables(rows):
    groups = defaultdict(list)
    for r in rows:
        if r["eligible_episode"] and r["both_described"]:
            groups[(r["physical_location"], r["payment"], r["network"])].append(r)
    result = []
    for (location, payment, network), group in sorted(groups.items()):
        result.append({
            "physical_location": location, "payment": payment, "network": network,
            "record_ids": [r["id"] for r in group],
            "account_keys": sorted({r["account"] for r in group}),
            "owner_keys": sorted({r["owner"] for r in group}),
            "sources": dict(Counter(r["source"] for r in group)),
            "latest_outcomes": dict(Counter(r["outcome"] for r in group)),
            "horizons": {str(h): {status: [r["id"] for r in group if r[f"horizon_{h}"] == status]
                                   for status in sorted(HORIZONS)} for h in (7, 30)},
        })
    return result


def analyze(data):
    rows = prepare(data)
    return {
        "as_of": data["as_of"], "inventory": inventory(rows), "joint_tables": joint_tables(rows),
        "possible_owner_links": data.get("possible_owner_links", []),
        "excluded_from_joint_table": [{"id": r["id"], "kind": r["kind"], "evidence": r["evidence"],
                                        "missing": [f for f in ("payment", "network") if r[f] == "unknown"]}
                                       for r in rows if not (r["eligible_episode"] and r["both_described"])],
        "without_each_source": {s: joint_tables([r for r in rows if r["source"] != s])
                                for s in sorted({r["source"] for r in rows})},
        "comparison_status": "Inventory and descriptive cells only. No ranked reliability, pooled-location denominator, or causal recommendation.",
        "owner_sensitivity_status": "No comparative effect estimated. Repeated owners are explicit in every cell; chronological owner-first selection awaits dated episode starts.",
    }


def main():
    raw = (ROOT / "cases.json").read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    out = analyze(data)
    out["input_sha256_lf_utf8"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    (ROOT / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Инвентаризация сочетаний", "",
             "Счетчики описывают записи этого добора и повторного аудита, не вероятность бана. РФ и неизвестное место разделены. Один аккаунт может иметь несколько эпизодов; исходы эпизодов не суммируются как люди.", "",
             "| Место | Оплата | Подключение | Записей / аккаунтных ключей / ключей владельцев | Последние исходы | 30 дней: работа / бан до срока / недостаточно данных | ID |",
             "|---|---|---|---|---|---|---|"]
    for t in out["joint_tables"]:
        h = t["horizons"]["30"]
        n = "/".join(str(len(t[k])) for k in ("record_ids", "account_keys", "owner_keys"))
        horizon = "/".join(str(len(h[k])) for k in ("worked_through_horizon", "ban_by_horizon", "insufficient"))
        outcomes = ", ".join(f"{k}:{v}" for k, v in sorted(t["latest_outcomes"].items()))
        lines.append(f"| {t['physical_location']} | {t['payment']} | {t['network']} | {n} | {outcomes} | {horizon} | {', '.join(t['record_ids'])} |")
    (ROOT / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(out["inventory"], ensure_ascii=False))


if __name__ == "__main__":
    main()
