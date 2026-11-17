"""Build the directly identified Russian subset and combine the two public batches."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MISSING_PAYMENT = {"", "Free", "Платежи из США, инструмент не назван","Разные способы, не уточняет"}


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter="\t"))


def write(path,rows,fields):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def summarize():
    all_rows=read(ROOT/"reports.tsv")
    ids=[r["record_id"] for r in all_rows]
    assert len(ids)==len(set(ids)) and all(r["outcome"] and r["primary_url"].startswith("https://") for r in all_rows)
    fields=list(all_rows[0])
    ru=[r for r in all_rows if r["cohort"]=="ru"]
    routes=[r for r in ru if r["purchase_or_attempt"] not in MISSING_PAYMENT and r["connection"]]
    write(ROOT/"russia.tsv",ru,fields)
    write(ROOT/"russia-routes.tsv",routes,fields)
    prior=next(p for p in [ROOT.parent/"public-collection-2026-11-17",ROOT.parent/"2026-11-17-public-reports"] if (p/"russia.tsv").exists())
    prev=read(prior/"russia.tsv")
    duplicate_ids=set(ids)&{r["record_id"] for r in read(prior/"observations.tsv")}
    assert not duplicate_ids, duplicate_ids
    old_routes={r["record_id"] for r in read(prior/"russia-payment-network.tsv")}
    translated=[]
    for r in prev:
        translated.append(dict(zip(fields,[r["record_id"],r["source"],r["observation_date"],"ru",r["russia_basis"],r["payment"],r["network"],
                                           r["duration_and_scope"],r["outcome"],r["note"],r["url"],r["support"]])))
    joint=translated+ru
    tagged=old_routes|{r["record_id"] for r in routes}
    write(ROOT/"both-rounds-russia.tsv",joint,fields)
    write(ROOT/"both-rounds-russia-routes.tsv",[r for r in joint if r["record_id"] in tagged],fields)
    stats={"new_reports":len(all_rows),"new_russia":len(ru),"new_russia_with_purchase_and_connection":len(routes),
           "new_by_source":dict(Counter(r["source"] for r in all_rows)),"new_russia_by_source":dict(Counter(r["source"] for r in ru)),
           "new_russia_outcomes":dict(Counter(r["outcome"] for r in ru)),
           "both_public_rounds_russia":len(joint),"both_public_rounds_russia_purchase_and_connection":len(tagged)}
    (ROOT/"counts.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return stats


if __name__=="__main__":
    print(summarize())
