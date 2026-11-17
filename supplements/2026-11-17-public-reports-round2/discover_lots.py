"""Find previously unseen public Claude product listings and collect their buyer reviews."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys

PARENT=Path(__file__).resolve().parent.parent
PRIOR=next(p for p in (PARENT/"public-collection-2026-11-17",PARENT/"2026-11-17-public-reports") if (p/"collect_market.py").exists())
sys.path.insert(0,str(PRIOR))
import collect_market as market

QUERIES=["Claude","Claude Pro","Claude Max","Claude Code","Anthropic","Клод","Клауд","Fable","Sonnet","Opus"]


def discover(q):
    items={}
    base={"query":q,"response":"json","pagesize":100}
    first=market.get("https://plati.io/api/search.ashx",{**base,"pagenum":1}).json()
    for i in range(1,first["Totalpages"]+1):
        page=first if i==1 else market.get("https://plati.io/api/search.ashx",{**base,"pagenum":i}).json()
        for x in page["items"]:
            if re.search(r"claude|anthropic|кл[ао]у?д",x["name"],re.I) and x["count_positiveresponses"]+x["count_negativeresponses"]:
                items[x["id"]]=x["name"]
    return items


if __name__=="__main__":
    cache=Path(sys.argv[1])
    market.CACHE=cache/"market"
    market.CACHE.mkdir(exist_ok=True,parents=True)
    already={r["product"] for r in json.loads((PRIOR/"market-coverage.json").read_text(encoding="utf-8"))}
    items={}
    with ThreadPoolExecutor(4) as ex:
        for found in ex.map(discover,QUERIES):
            items.update(found)
    products=sorted(items.keys()-already)
    print("New listings:",len(products),flush=True)
    collected=[]
    with ThreadPoolExecutor(4) as ex:
        for pid,future in [(p,ex.submit(market.reviews,p)) for p in products]:
            try:
                item=future.result()
                if item:
                    collected.append(item)
            except Exception as err:
                collected.append({"product":pid,"error":str(err)[:130]})
    (cache/"market-extra.json").write_text(json.dumps(collected,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Reviews:",sum(r.get("reviews_read",0) for r in collected))
