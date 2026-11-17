"""Scan international Play reviews for first-person references to Russia."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys
from collect_reviews import ANDROID

REGION=re.compile(r"russi|rusland|russland|russisch|russie|moscow|moscou|moskau|moskva|st\.? petersburg|росси|росій|росія|москв|петербург|паспорт.{0,6}рф|\bрф\b|rusya|rus vatanda|федерации",re.I)


def collect(args):
    from google_play_scraper import Sort,reviews
    lang,country=args
    seen=set()
    hits=[]
    token=None
    date=""
    error=""
    for page in range(1,501):
        try:
            rows,token=reviews(ANDROID,lang=lang,country=country,count=200,sort=Sort.NEWEST,continuation_token=token)
        except Exception as exc:
            error=str(exc)[:150]
            break
        added=0
        for row in rows:
            rid=row["reviewId"]
            if rid in seen:
                continue
            seen.add(rid)
            added+=1
            t=row["content"] or ""
            date=row["at"].date().isoformat()
            if REGION.search(t):
                hits.append({"key":"gp-"+rid,"date":date,"text":t,"url":f"https://play.google.com/store/apps/details?id={ANDROID}&reviewId={rid}&hl={lang}"})
        if not added or not getattr(token,"token",None) or (date and date<"2025-01-01"):
            break
    return hits,{"language":lang,"country":country,"unique_read":len(seen),"region_hits":len(hits),"last_date":date,"pages":page,"error":error}


if __name__=="__main__":
    cache=Path(sys.argv[1])
    sys.path.insert(0,sys.argv[2])
    with ThreadPoolExecutor(6) as pool:
        parts=list(pool.map(collect,[("en","us"),("uk","ua"),("de","de"),("fr","fr"),("tr","tr"),("kk","kz"),("be","by")]))
    hits={r["key"]:r for items,_ in parts for r in items}
    (cache/"international.json").write_text(json.dumps(list(hits.values()),ensure_ascii=False),encoding="utf-8")
    (cache/"international-coverage.json").write_text(json.dumps([m for _,m in parts],ensure_ascii=False,indent=2),encoding="utf-8")
    print([m for _,m in parts],flush=True)
