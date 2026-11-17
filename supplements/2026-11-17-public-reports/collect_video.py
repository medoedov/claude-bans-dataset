"""Search public YouTube pages and read comments on relevant Russian-language videos."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

import requests

ROOT = Path(__file__).resolve().parent
CACHE = Path(tempfile.gettempdir()) / "claude-video-public-20261117"
sys.path.insert(0, str(Path(tempfile.gettempdir()) / "claude-public-comments-nov17"))
from youtube_comment_downloader import YoutubeCommentDownloader

QUERIES = ["Claude верификация паспорт блокировки Россия", "Claude Code забанили аккаунт из России", "Claude Pro оплатить подписку из России", "Claude Code из России VPS VPN оплата", "Claude банит аккаунт октябрь 2026 Клод"]
SEEDS = ["tGS2GKI2YHg", "sAvDqBKB8MY", "WgVifeEt-TQ", "HmWcJZ4GAZ8", "BLSxXOeSB1o", "PZKCYLfOVh0"]


def discover(q):
    resp = requests.get("https://www.youtube.com/results", params={"search_query":q,"hl":"ru"}, timeout=25)
    resp.raise_for_status()
    match = re.search(r'(?:var\s+ytInitialData|window\["ytInitialData"\])\s*=\s*', resp.text)
    if not match:
        raise ValueError("No public search data")
    data, _ = json.JSONDecoder().raw_decode(resp.text[match.end():])
    results = {}
    for item in YoutubeCommentDownloader.search_dict(data, "videoRenderer"):
        title = "".join(x["text"] for x in item["title"].get("runs", []))
        if re.search(r"claude|кл[оа]у?д",title,re.I) and re.search(r"бан|блок|аккаунт|оплат|подпис|росси|карт|провер|вериф|регистр|паспорт|доступ|vpn|vps|рф",title,re.I):
            results[item["videoId"]] = title
    return results


def collect(vid):
    known = set()
    reader = YoutubeCommentDownloader()
    target = CACHE / (vid+".jsonl")
    old = Path(tempfile.gettempdir()) / ("claude-yt-public-"+vid+".jsonl")
    if vid in SEEDS and old.exists() and old.stat().st_size:
        # Reuse the first seed pass when finished.
        for line in old.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            known.add(item["cid"])
        return {"n":len(known),"cache":"seed"}
    try:
        with target.open("w", encoding="utf-8") as f:
            for item in reader.get_comments(vid, language="en"):
                if item["cid"] in known:
                    continue
                known.add(item["cid"])
                row = {k:item.get(k) for k in ("cid","text","time","reply")}
                row["author_key"] = hashlib.sha256(item["channel"].encode()).hexdigest()[:20]
                f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return {"n":len(known),"cache":"video"}
    except (RuntimeError, ValueError, KeyError, requests.RequestException) as exc:
        return {"n":len(known),"error":str(exc)[:140],"cache":"video"}


if __name__ == "__main__":
    CACHE.mkdir(exist_ok=True)
    videos = dict.fromkeys(SEEDS,"Заданная ссылка")
    errors = {}
    for q in QUERIES:
        try:
            videos.update(discover(q))
        except (ValueError, requests.RequestException) as exc:
            errors[q] = str(exc)
    print("video candidates:",len(videos),flush=True)
    coverage = {}
    with concurrent.futures.ThreadPoolExecutor(5) as pool:
        tasks = {pool.submit(collect,vid):vid for vid in videos}
        for task in concurrent.futures.as_completed(tasks):
            vid = tasks[task]
            coverage[vid] = {"title":videos[vid],**task.result()}
            (ROOT/"video-coverage.json").write_text(json.dumps({"search_errors":errors,"videos":coverage},ensure_ascii=False,indent=2),encoding="utf-8")
    print("videos:",len(coverage),"comments:",sum(r["n"] for r in coverage.values()))
