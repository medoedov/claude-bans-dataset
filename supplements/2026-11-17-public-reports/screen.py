"""Build a private reading queue and export public, manually adjudicated observations."""
import csv
import hashlib
import json
from pathlib import Path
import os
import re
import tempfile


ROOT = Path(__file__).resolve().parent
TMP = Path(os.environ.get("CLAUDE_COLLECTION_CACHE",tempfile.gettempdir()))
GROUPS = {
    "region":r"росси[ийюя]|россиян|\bрф\b|москв|питер|екатеринб|спб|казан[иь]|загранник РФ|russia",
    "pay":r"карт[ауыоые]|банк[а-я]*|ап[п]?\s?стор|app\s?store|apple\s?(id|pay)|гугл\s?пл|google\s?(play|pay)|посредник|селлер|продав[ецц]|ggsel|plati|плати[. ]|playerok|гифт|gift|подарочн|криптокарт|paypa[lл]|виртуалк",
    "net":r"\b(vpn|vps|vds|dns|isp|впн|впс|днс|proxy|vless|ip)\b|прокс[иья]|сервер|айпи|тунне?л|тонне?л|резидентск|резиден[тц]иальн",
    "time":r"месяц|недел|полгод|год[аау]?\b|\d+\s*(дня|день|дней|суток|час)|через.{0,12}(день|сутки|минут|час)|сразу|мгновенн|продл[иея]|продле|на следующий день",
    "event":r"забан|забло[кч]|блокир|\bбан\b|\bбан[аыеу]\b|кикнул|отлетел|снесли|вериф|kyc|паспорт|личност|работа[еюл]|пользуюсь|пользовался|продлил|продлеваю|восстанов|возврат|летает|полет норм|полёт норм|жив[её]т",
}
RX = {k:re.compile(v,re.I) for k,v in GROUPS.items()}


def flags(s):
    return {k for k,v in RX.items() if v.search(s)}


def sources():
    for p in sorted((TMP/"claude-market-public-20261117").glob("*.jsonl")):
        for line in p.open(encoding="utf-8"):
            r=json.loads(line)
            yield ("m"+str(r["id"]),r["text"],str(r["date"]),f"https://api.digiseller.com/api/reviews?seller_id={r['seller']}&product_id={r['pid']}&type=all&page={r['page']}&rows=500",str(r["pid"]),"")
    vids = list(TMP.glob("claude-yt-public-*.jsonl"))+list((TMP/"claude-video-public-20261117").glob("*.jsonl"))
    for p in sorted(vids):
        vid=p.stem.removeprefix("claude-yt-public-")
        for line in p.open(encoding="utf-8"):
            r=json.loads(line)
            owner=r.get("author_key") or hashlib.sha256(r.get("author","").casefold().encode()).hexdigest()[:20]
            yield (r["cid"],r["text"],r["time"],f"https://www.youtube.com/watch?v={vid}&lc={r['cid']}",vid,owner)


def load():
    return {r[0]:r for r in sources()}


def queue(records):
    seen=set()
    hits=[]
    for key,txt,stamp,url,src,owner in records.values():
        hit=flags(txt)
        norm=" ".join(txt.lower().split())
        if not txt or norm in seen:
            continue
        seen.add(norm)
        if "event" not in hit:
            continue
        if key.startswith("m"):
            # In marketplace reviews a purchase channel is known, regardless of card type.
            if not (hit & {"region","net"} or re.search(r"забанили|заблокировали|отлетел|паспорт|загран|верификац|второй месяц|третий месяц|четв[её]ртый месяц|пятый месяц|полгода|\d+ месяц",txt,re.I)):
                continue
        elif not (hit & {"region","net","pay"} and len(hit)>=3):
            continue
        hits.append((key," ".join(sorted(hit)),txt))
    return hits


if __name__=="__main__":
    rows=load()
    hits=queue(rows)
    with (TMP/"claude-screened-20261117.json").open("w",encoding="utf-8") as f:
        json.dump(hits,f,ensure_ascii=False)
    print("source rows",len(rows),"shortlisted",len(hits))
