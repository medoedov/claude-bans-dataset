"""Descriptive option comparisons, never a population ban-risk estimate."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PRIMARY = {
    "network": ("access_ip", {"datacenter_vps"}, {"commercial_vpn"}),
    "plan": ("plan", {"max20"}, {"pro", "max5"}),
    "payment": ("payment_method", {"own_card_foreign"}, {"reseller"}),
    "usage": ("usage", {"heavy"}, {"normal"}),
}
SECONDARY = {
    "stable": ("ip_stable", {"yes"}, {"no"}),
    "appstore_vs_reseller": ("payment_method", {"app_store"}, {"reseller"}),
    "virtual_vs_bank": ("payment_method", {"virtual_card"}, {"own_card_foreign"}),
    "young_vs_old": ("age_bin", {"0_to_1"}, {"over_12"}),
}
SURVIVING = {"active", "survived"}


def fisher(a, b, c, d):
    """Two-sided Fisher; formula reused from first article's groups.py."""
    n, r1, c1 = a + b + c + d, a + b, a + c
    p0 = math.comb(c1, a) * math.comb(n - c1, r1 - a) / math.comb(n, r1)
    return min(1.0, sum(
        p for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1)
        if (p := math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)) <= p0 * (1 + 1e-9)
    ))


def wilson(k, n):
    if not n:
        return None
    z = 1.959963984540054
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0, center - half), min(1, center + half)]


def holm(values):
    result, running = {}, 0
    for rank, (key, value) in enumerate(sorted(values.items(), key=lambda kv: kv[1] if kv[1] is not None else 1)):
        running = max(running, min(1, (len(values) - rank) * (value if value is not None else 1)))
        result[key] = running if value is not None else None
    return result


def thread_key(case):
    """No comment IDs: resamples must not pretend each comment is a source."""
    url = case.get("url", "").split(";")[0]
    parts = urlsplit(url)
    path = parts.path.rstrip("/")
    if "habr.com" in parts.netloc:
        path = path.split("/comments")[0]
    if "reddit.com" in parts.netloc:
        chunks = path.split("/")
        if "comments" in chunks:
            path = "/".join(chunks[:chunks.index("comments") + 2])
    return parts.netloc + path if parts.netloc else "private:" + case.get("source", "unknown")


def prepare(data, overrides):
    records = data["base_records"]
    ids = {r["case"]["case_id"] for r in records}
    if len(ids) != len(records):
        raise ValueError("Duplicate base case")
    parent = {cid: cid for cid in ids}

    def find(cid):
        while parent[cid] != cid:
            parent[cid] = parent[parent[cid]]
            cid = parent[cid]
        return cid

    def link(a, b):
        if a not in ids or b not in ids:
            raise ValueError(f"Unknown related case: {a}, {b}")
        x, y = find(a), find(b)
        parent[max(x, y)] = min(x, y)

    for r in records:
        for detail in r["details"]:
            for cid in json.loads(detail["details_json"]).get("related_case_ids", []):
                link(r["case"]["case_id"], cid)
    for decision in data["review_decisions"]:
        related = decision.get("existing_case_ids", [])
        for cid in related[1:]:
            link(related[0], cid)
    for related in overrides.get("dependency_links", []):
        for cid in related[1:]:
            link(related[0], cid)
    fixes = {x["case_id"]: x for x in overrides["overrides"]}
    if set(fixes) - ids:
        raise ValueError("Override refers to unknown case")
    rows, exclusions = [], []
    for record in records:
        c = dict(record["case"])
        cid = c["case_id"]
        fix = fixes.get(cid, {})
        c.update(fix.get("fields", {}))
        reason = None
        if fix.get("exclude") or record["unit"] == "owner_aggregate":
            reason = "aggregate_or_not_individual"
        elif c["plan"] in {"api", "team", "enterprise"} or c["product"] in {"console_api", "team_organization"}:
            reason = "not_consumer"
        elif c["cohort"] == "addition" and (c["product"] != "consumer" or c["evidence_class"] != "firsthand"):
            reason = "addition_not_consumer_firsthand"
        if reason:
            exclusions.append({"case_id": cid, "reason": reason})
            continue
        region = c["user_region"].lower()
        c["location"] = "recorded_RU" if region == "ru" else "unknown_location" if region in {"unknown", ""} else "known_abroad"
        c["collection"] = "addition" if c["cohort"] == "addition" else "legacy"
        c["plan_bin"] = "max20" if c["plan"] == "max20" else "pro_max5" if c["plan"] in {"pro", "max5"} else "other_unknown"
        c["source_family"] = "telegram" if "telegram" in c["source"] else c["source"]
        c["thread"] = thread_key(c)
        c["component"] = find(cid)
        try:
            age = float(c["account_age_months"])
            c["age_bin"] = "0_to_1" if 0 <= age <= 1 else "over_12" if age > 12 else "1_to_12" if age > 1 else "unknown"
        except (TypeError, ValueError):
            c["age_bin"] = "unknown"
        observed = c.get("last_observed_at") or c.get("post_date", "")
        c["late_observation"] = "yes" if "2026-10-29" <= observed[:10] <= "2026-11-06" else "no"
        c["confirmed_prior_ban"] = any(e["event"] == "banned" for e in record["events"])
        rows.append(c)
    return rows, exclusions


def compare(rows, pair, endpoint="banned", one_per_component=False):
    field, av, bv = pair
    if av & bv:
        raise ValueError("Comparison alternatives overlap")
    known = [r for r in rows if r.get(field) in av | bv]
    if one_per_component:
        representatives = {}
        for r in sorted(known, key=lambda r: r["case_id"]):
            representatives.setdefault(r["component"], r)
        known = list(representatives.values())
    result = {"eligible_rows": len(rows), "missing_or_other_factor": sum(r.get(field) not in av | bv for r in rows),
              "known_rows": len(known), "known_components": len({r["component"] for r in known}), "endpoint": endpoint}
    for name, values in (("a", av), ("b", bv)):
        selected = [r for r in known if r[field] in values]
        ban_ids = [r["case_id"] for r in selected if r["outcome"] == "banned"
                   or endpoint == "banned_or_locked" and r["outcome"] == "locked"
                   or endpoint == "documented_prior_ban" and r["outcome"] in SURVIVING | {"unbanned"} and r["confirmed_prior_ban"]]
        active_ids = [r["case_id"] for r in selected if r["outcome"] in SURVIVING and r["case_id"] not in ban_ids]
        n, k = len(ban_ids) + len(active_ids), len(ban_ids)
        result[name] = {"values": sorted(values), "outcomes": dict(Counter(r["outcome"] for r in selected)),
                        "banned": k, "active": len(active_ids), "n": n, "fraction": k / n if n else None,
                        "wilson95": wilson(k, n), "ban_ids": ban_ids, "active_ids": active_ids,
                        "age_known": sum(r["age_bin"] != "unknown" for r in selected)}
    a, b = result["a"], result["b"]
    if a["n"] and b["n"]:
        result["difference_pp"] = 100 * (a["fraction"] - b["fraction"])
        result["fraction_ratio"] = a["fraction"] / b["fraction"] if b["fraction"] else None
        result["fisher_p"] = fisher(a["banned"], a["active"], b["banned"], b["active"])
    else:
        result.update(difference_pp=None, fraction_ratio=None, fisher_p=None)
    return result


def analyze(rows):
    tables = []
    populations = {
        "recorded_RU": [r for r in rows if r["location"] == "recorded_RU"],
        "context_compatible": [r for r in rows if r["location"] != "known_abroad"],
        "unknown_location": [r for r in rows if r["location"] == "unknown_location"],
    }
    for population, pool in populations.items():
        for collection in ("all", "legacy", "addition"):
            sample = pool if collection == "all" else [r for r in pool if r["collection"] == collection]
            for name, pair in (PRIMARY | SECONDARY).items():
                views = [("all", sample, "banned", False),
                         ("one_per_component", sample, "banned", True),
                         ("banned_or_locked", sample, "banned_or_locked", False),
                         ("documented_prior_ban", sample, "documented_prior_ban", False)]
                if name in PRIMARY or name == "appstore_vs_reseller":
                    matching = [r for r in sample if r.get(pair[0]) in pair[1] | pair[2]]
                    threads = Counter(r["thread"] for r in matching)
                    largest = sorted(threads, key=lambda key: (-threads[key], key))[0] if threads else None
                    views.append(("without_largest_thread", [r for r in sample if r["thread"] != largest], "banned", False))
                    views.append(("known_consumer", [r for r in sample if r["product"] == "consumer"], "banned", False))
                    views.append(("wave_oct01", [r for r in sample if r["wave"] == "2026-10-01"], "banned", False))
                    views.append(("late_observations", [r for r in sample if r["late_observation"] == "yes"], "banned", False))
                    stratifier = "usage" if name == "plan" else "plan_bin"
                    for value in sorted({r[stratifier] for r in sample}):
                        views.append((stratifier + "=" + value, [r for r in sample if r[stratifier] == value], "banned", False))
                    for value in sorted({r["source_family"] for r in matching}):
                        views.append(("source=" + value, [r for r in sample if r["source_family"] == value], "banned", False))
                for view, selected, endpoint, single in views:
                    result = compare(selected, pair, endpoint, single)
                    result.update(population=population, collection=collection, comparison=name, view=view)
                    if view == "without_largest_thread":
                        result["excluded_thread"] = largest
                    tables.append(result)
    family = {r["comparison"]: r["fisher_p"] for r in tables if r["population"] == "recorded_RU" and r["collection"] == "all" and r["view"] == "all" and r["comparison"] in PRIMARY}
    adjusted = holm(family)
    for r in tables:
        if r["population"] == "recorded_RU" and r["collection"] == "all" and r["view"] == "all" and r["comparison"] in PRIMARY:
            r["holm_p_four_primary"] = adjusted[r["comparison"]]
    return tables


def main():
    paths = [ROOT / "integrated.json", ROOT / "statistics-overrides.json", ROOT / "statistics-extra-overrides.json"]
    data, overrides, extra = [json.loads(p.read_text(encoding="utf-8-sig")) for p in paths]
    overrides["overrides"].extend(extra["overrides"])
    overrides["dependency_links"] = extra["dependency_links"]
    rows, exclusions = prepare(data, overrides)
    tables = analyze(rows)
    output = {"as_of": "2026-11-07", "interpretation": "Descriptive self-reported stories, not population incidence or causal effects.",
              "input_sha256_lf_utf8": {p.name: hashlib.sha256(p.read_text(encoding="utf-8-sig").encode()).hexdigest() for p in paths},
              "included_rows": len(rows), "locations": dict(Counter(r["location"] for r in rows)),
              "exclusions": exclusions, "tables": tables}
    (ROOT / "option-comparisons.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["case_id", "collection", "location", "plan", "usage", "access_ip", "payment_method", "ip_stable", "age_bin", "outcome", "component", "source_family", "thread", "last_observed_at"]
    with (ROOT / "statistics-cases.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Сравнение вариантов: описательная статистика", "", "Числитель — banned; знаменатель — banned+active+survived. Остальные исходы и ID лежат в JSON. Доля среди рассказавших не является вероятностью бана.", "",
             "| Срез | Сбор | Сравнение A/B | A: бан/известный исход | B: бан/известный исход | Разница, п.п. |", "|---|---|---|---|---|---|"]
    for r in tables:
        if r["view"] == "all" and r["population"] != "unknown_location":
            a, b = r["a"], r["b"]
            diff = f'{r["difference_pp"]:.1f}' if r["difference_pp"] is not None else "нет"
            lines.append(f'| {r["population"]} | {r["collection"]} | {r["comparison"]} | {a["banned"]}/{a["n"]} | {b["banned"]}/{b["n"]} | {diff} |')
    (ROOT / "option-comparisons.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"included_rows": len(rows), "locations": output["locations"], "tables": len(tables)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
