"""Read public buyer review panels for sellers listed in two Claude categories."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import sys

import requests
from bs4 import BeautifulSoup


def panel(http,offer):
    r=http.get(offer,timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.content,"html.parser").select_one("#reviews")


def collect(seller,offer):
    result={}
    count=0
    pages=0
    error=""
    try:
        with requests.Session() as http:
            block=panel(http,offer)
            for page in range(1,9):
                if block is None:
                    break
                seen_here=0
                items=block.select(".review-item")
                if not items:
                    break
                pages+=1
                for item in items:
                    text=item.select_one(".review-compiled-review .review-item-text")
                    category=item.select_one(".review-item-detail")
                    date=item.select_one(".review-item-date")
                    if category is None or text is None:
                        continue
                    count+=1
                    detail=category.get_text(" ",strip=True)
                    body=text.get_text(" ",strip=True)
                    if not re.search(r"claude|кл[оа]у?д",detail,re.I) or not body:
                        continue
                    key=hashlib.sha256((seller+"|"+body.casefold()).encode()).hexdigest()[:24]
                    result[key]={"key":"fp-"+key,"text":body,"date":date.get_text(" ",strip=True) if date else "",
                                 "seller":seller,"offer":offer,"category":detail,"page":page}
                    seen_here+=1
                form=block.select_one("form.dyn-table-form")
                if not form or page==8 or (page>1 and not seen_here):
                    break
                params={i["name"]:i.get("value","") for i in form.select("input[name]") if i["name"] in {"user_id","continue","filter"}}
                if not params.get("continue"):
                    break
                # This is the site's public "show more reviews" form.
                response=http.post("https://funpay.com/users/reviews",data=params,headers={"X-Requested-With":"XMLHttpRequest"},timeout=12)
                response.raise_for_status()
                if "json" in response.headers.get("Content-Type",""):
                    payload=response.json()
                    html=payload.get("html","") if isinstance(payload,dict) else ""
                else:
                    html=response.text
                block=BeautifulSoup(html,"html.parser")
    except (ValueError,requests.RequestException) as exc:
        error=str(exc)[:140]
    return list(result.values()),{"seller":seller,"offer":offer,"review_pages":pages,"all_text_entries_seen":count,"claude":len(result),"error":error}


if __name__=="__main__":
    cache=Path(sys.argv[1])
    offers={}
    for number in (3173,3172):
        u=f"https://funpay.com/lots/{number}/"
        r=requests.get(u,timeout=20)
        r.raise_for_status()
        for a in BeautifulSoup(r.content,"html.parser").select("a.tc-item[data-user][href]"):
            if a.select_one(".rating-mini-count"):
                offers.setdefault(a["data-user"],a["href"])
    print("seller panels",len(offers),flush=True)
    metadata=[]
    with ThreadPoolExecutor(5) as pool,(cache/"funpay.jsonl").open("w",encoding="utf-8") as f:
        futures=[pool.submit(collect,k,u) for k,u in offers.items()]
        for future in as_completed(futures):
            rows,meta=future.result()
            for row in rows:
                f.write(json.dumps(row,ensure_ascii=False)+"\n")
            f.flush()
            metadata.append(meta)
    (cache/"funpay-coverage.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Claude category",sum(m["claude"] for m in metadata))
