"""Collect public buyer reviews, keeping order numbers and seller replies out of the cache."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import re
import tempfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parent
CACHE = Path(tempfile.gettempdir()) / "claude-market-public-20261117"
API = "https://api.digiseller.com/api/"


def get(url, params=None):
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 502, 503, 504], allowed_methods=["GET"])))
        response = session.get(url, params=params, headers={"Accept": "application/json, text/html"}, timeout=25)
        response.raise_for_status()
        return response


def discover():
    ids = {4023986, 6313782, 5817327}
    url = "https://plati.io/api/search.ashx"
    params = {"query":"Claude","response":"json","pagesize":100,"pagenum":1}
    first = get(url,params).json()
    for page in range(1, first["Totalpages"]+1):
        batch = first if page==1 else get(url,{**params,"pagenum":page}).json()
        for item in batch["items"]:
            name = item["name"]
            if (re.search(r"claude",name,re.I) and re.search(r"pro|max|ultra|подпис",name,re.I)
                    and not re.search(r"api|gpt|gemini|cursor|vpn|прокси|perplexity|codex",name,re.I)
                    and item["count_positiveresponses"]+item["count_negativeresponses"]>0):
                ids.add(item["id"])
    return sorted(ids)


def reviews(pid):
    p = get(f"{API}products/{pid}/data").json().get("product") or {}
    if "claude" not in str(p.get("name", "")).lower():
        return None
    sid = p["seller"]["id"]
    params = {"product_id": pid, "seller_id": sid, "type": "all", "rows": 500}
    first = get(API+"reviews", {**params, "page": 1}).json()
    if first.get("retval") != 0:
        raise ValueError(first.get("retdesc"))
    seen = set()
    with (CACHE / f"{pid}.jsonl").open("w", encoding="utf-8") as out:
        for page in range(1, first["totalPages"]+1):
            result = first if page == 1 else get(API+"reviews", {**params, "page": page}).json()
            if result.get("retval") != 0:
                raise ValueError(result.get("retdesc"))
            for item in result.get("review", []):
                rid = item["id"]
                if rid in seen:
                    continue
                seen.add(rid)
                data = {"id":rid,"pid":pid,"seller":sid,"page":page,"date":item["dateUtc"],"text":item.get("info","")}
                out.write(json.dumps(data,ensure_ascii=False)+"\n")
    return {"product":pid,"seller":sid,"title":p["name"],"reviews_read":len(seen),"listed_at_start":first["totalItems"],"pages":first["totalPages"],"sha256":hashlib.sha256((CACHE / f"{pid}.jsonl").read_bytes()).hexdigest()}


if __name__ == "__main__":
    CACHE.mkdir(exist_ok=True)
    products = discover()
    coverage = []
    manifest = ROOT / "market-coverage.json"
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    cached = {r["product"]:r for r in previous if "sha256" in r and (CACHE/f"{r['product']}.jsonl").exists()
              and hashlib.sha256((CACHE/f"{r['product']}.jsonl").read_bytes()).hexdigest()==r["sha256"]}
    coverage.extend(cached[p] for p in products if p in cached)
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks = [(pid, pool.submit(reviews, pid)) for pid in products if pid not in cached]
        for pid, task in tasks:
            try:
                row = task.result()
                if row:
                    coverage.append(row)
            except (ValueError, requests.RequestException) as exc:
                coverage.append({"product":pid,"error":str(exc)})
    (ROOT / "market-coverage.json").write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding="utf-8")
    print([(r["product"],r.get("reviews_read",r.get("error"))) for r in coverage])
