"""Count source reports and explicitly identified Russian owners separately."""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIRECT = {"документ РФ","из РФ","гражданство РФ","из РФ, документ РФ","из РФ, самоописание РФ","самоописание РФ","возвращается в РФ"}
UNSPECIFIED_PAY = {"","Free","До оплаты","Один способ, вид не назван","Оплата из Сингапура, инструмент не назван","Платежный профиль США","Оплата с телефона, инструмент неизвестен","не установлен для старого аккаунта","Куплен аккаунт без подписки"}
WORKING = {"работает","без бана на дату отзыва","без бана на дату сообщения","работал до конца срока"}
BANNED = {"бан","бан после KYC","бан и возврат"}
CALENDAR = re.compile(r"час|минут|сут[окиа]|сутк|день|дне[йм]|дня|два дня|недел|месяц|полгод|\bгод|лет|январ|феврал|март|апрел|ма[яй]|июн|июл|август|сентябр|октябр|ноябр|декабр|202[3456]|дн[яе]",re.I)


def summarize():
    with (ROOT/"observations.tsv").open(encoding="utf-8-sig",newline="") as f:
        records=list(csv.DictReader(f,delimiter="\t"))
    direct=[r for r in records if r["russia_basis"] in DIRECT]
    def stats(rows):
        pay_net=[r for r in rows if r["payment"] not in UNSPECIFIED_PAY and r["network"]]
        timed=[r for r in pay_net if CALENDAR.search(r["duration_and_scope"])]
        return dict(reports=len(rows),by_source=dict(Counter(r["source"] for r in rows)),payment_network=len(pay_net),
                    payment_network_time=len(timed),timed_working=sum(r["outcome"] in WORKING for r in timed),
                    timed_banned=sum(r["outcome"] in BANNED for r in timed),
                    outcomes=dict(Counter(r["outcome"] for r in rows)))
    result={"all":stats(records),"explicit_russia":stats(direct)}
    for name,rows in [("russia",direct),("russia-payment-network",[r for r in direct if r["payment"] not in UNSPECIFIED_PAY and r["network"]])]:
        with (ROOT/(name+".tsv")).open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.DictWriter(f, fieldnames=records[0].keys(),delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
    (ROOT/"counts.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for k,v in result.items():
        print(k, {f:n for f,n in v.items() if f!="outcomes"})


if __name__=="__main__":
    summarize()
