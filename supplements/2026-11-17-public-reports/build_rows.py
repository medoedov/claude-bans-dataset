"""Resolve manually selected review/comment IDs against the observed public response."""
import csv
import hashlib
from datetime import datetime
from screen import ROOT, load, queue


FIELDS = ["record_id","source","observation_date","russia_basis","payment","network","duration_and_scope","outcome","note","url","support","public_owner_key"]


def build():
    source=load()
    if not source:
        raise RuntimeError("Missing source cache; see README.md")
    with (ROOT/"bulk-duration-review.tsv").open(encoding="utf-8-sig",newline="") as f:
        periods={r["record_id"]:r for r in csv.DictReader(f, delimiter="\t")}
    rows=[]
    decisions=[s.split("\t") for s in (ROOT/"decisions.tsv").read_text(encoding="utf-8-sig").splitlines() if s]
    selected={r[0] for r in decisions}
    for key in periods.keys()-selected:
        decisions.append([key,"контекст площадки","","","","",""])
    for key,basis,pay,net,period,outcome,note in sorted(decisions):
        if key in periods:
            audited=periods[key]
            period=period or audited["duration_and_scope"]
            outcome=outcome or audited["outcome"]
            if audited["note"] and audited["note"] not in note:
                note=(note+" "+audited["note"]).strip()
        if key=="m17720469":
            net="без VPN"
        if key=="m18202708":
            pay="Через продавца, активация в iOS"
        if key in {"m18227825","m18195926"}:
            basis="документ РФ"
        _,_,stamp,url,product,owner=source[key]
        if key.startswith("m"):
            stamp=datetime.strptime(stamp,"%d.%m.%Y %H:%M:%S").date().isoformat()
            platform="DigiSeller"
            link=f"https://plati.market/itm/{product}"
            if not pay:
                pay="Покупка через продавца лота"
        else:
            platform="YouTube"
            stamp=stamp+" (относительно даты сбора 17.11.2026)"
            link=""
        rows.append([key,platform,stamp,basis,pay,net,period,outcome,note,url,link,owner])
    with (ROOT/"community.tsv").open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            rows.append([row.get(k,"") for k in FIELDS])
    ids=[r[0] for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("Duplicate public record ID")
    owners=[row[-1] for row in rows if row[-1]]
    if len(owners)!=len(set(owners)):
        raise ValueError("Review repeated owner keys before release")
    for row in rows:
        if not row[0] or not row[7] or not row[9].startswith("https://"):
            raise ValueError(row[:2])
        row[-1]=""
    with (ROOT/"observations.tsv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter="\t")
        writer.writerow(FIELDS)
        writer.writerows(rows)
    selected=set(ids)
    with (ROOT/"candidate-index.tsv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter="\t")
        writer.writerow(["record_id","source_id","flags","included","text_sha256","url_at_collection"])
        for key,flags,txt in queue(source):
            writer.writerow([key,source[key][4],flags,int(key in selected),hashlib.sha256(txt.encode()).hexdigest(),source[key][3]])


if __name__=="__main__":
    build()
