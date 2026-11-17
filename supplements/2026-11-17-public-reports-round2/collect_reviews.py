"""Collect public consumer reviews of the official Android and iOS Claude apps."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys

import requests

APPLE_ID = "6473753684"
ANDROID = "com.anthropic.claude"
STOREFRONTS = "ru kz ua by am uz kg ge az md tr cy rs me il de gb us fi lv ee lt pl es nl ae".split()


def collect_apple(country):
    result = {}
    info = {"country":country, "pages":0}
    for page in range(1,11):
        url=f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={APPLE_ID}/sortby=mostrecent/json"
        try:
            response=requests.get(url,timeout=18)
            response.raise_for_status()
            obj=response.json()["feed"]
        except (requests.RequestException,ValueError,KeyError) as err:
            info["error"]=str(err)[:160]
            break
        entries=obj.get("entry",[])
        if isinstance(entries,dict):
            entries=[entries]
        info["pages"]+=1
        new=0
        for item in entries:
            if "im:rating" not in item:
                continue
            key=item["id"]["label"]
            if key not in result:
                new+=1
            result[key]={"key":"ios-"+key,"date":item["updated"]["label"][:10],
                         "text":item["title"]["label"]+". "+item["content"]["label"],
                         "url":f"https://apps.apple.com/{country}/app/id{APPLE_ID}?see-all=reviews&platform=iphone&reviewId={key}","feed":url}
        if not new or len(entries)<50:
            break
    return list(result.values()),info


def collect_google(cache, lib):
    if lib:
        sys.path.insert(0,lib)
    from google_play_scraper import Sort,reviews
    rows={}
    coverage=[]
    for country in "ru kz ua by us de".split():
        token=None
        info={"country":country,"pages":0}
        for _ in range(120):
            try:
                entries,token=reviews(ANDROID,lang="ru",country=country,sort=Sort.NEWEST,count=200,continuation_token=token)
            except Exception as err:
                info["error"]=str(err)[:140]
                break
            info["pages"]+=1
            added=0
            for item in entries:
                key=item["reviewId"]
                if key not in rows:
                    added+=1
                rows[key]={"key":"gp-"+key,"date":item["at"].date().isoformat(),"text":item["content"] or "",
                           "url":f"https://play.google.com/store/apps/details?id={ANDROID}&reviewId={key}&hl=ru"}
            if not entries or not getattr(token,"token",None) or (country!="ru" and not added):
                break
        info["cumulative_unique"]=len(rows)
        coverage.append(info)
    save(cache,"google",list(rows.values()),coverage)


def save(cache,name,rows,coverage):
    path=cache/(name+".jsonl")
    with path.open("w",encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row,ensure_ascii=False)+"\n")
    meta={"reviews":len(rows),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"coverage":coverage}
    (cache/(name+"-coverage.json")).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print(name,len(rows),flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["apple","google"])
    ap.add_argument("cache",type=Path)
    ap.add_argument("--lib")
    args=ap.parse_args()
    args.cache.mkdir(parents=True,exist_ok=True)
    if args.mode=="apple":
        with ThreadPoolExecutor(6) as ex:
            parts=list(ex.map(collect_apple,STOREFRONTS))
        rows={r["key"]:r for items,_ in parts for r in items}
        save(args.cache,"apple",list(rows.values()),[meta for _,meta in parts])
    else:
        collect_google(args.cache,args.lib)
