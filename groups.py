"""Главный расчёт главы «Кого банят»: группы РФ / Китай+Гонконг / остальной мир, признаки забаненных и выживших,
точный тест Фишера для 2×2, возвраты, апелляции, новые аккаунты, волны. Вход — cases.csv.
Выход — groups.md и charts/*.png."""
from math import comb
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
d = pd.read_csv(HERE / "cases.csv", dtype=str, keep_default_na=False)
for c in d.columns:
    if c not in ("case_id", "url", "notes", "post_date", "ban_date", "wave", "account_age_months", "group"):
        d[c] = d[c].str.strip().str.lower().replace("", "unknown")
d["date"] = pd.to_datetime(d["ban_date"].where(d["ban_date"] != "", d["post_date"]), errors="coerce")
d["automation"] = d["automation"].str.split(";").str[0]
d["age"] = pd.to_numeric(d["account_age_months"], errors="coerce")


d["group"] = d["group"].map({"RU": "РФ", "CN": "Китай и Гонконг", "WORLD": "мир"})
d["is_ban"] = d["outcome"].isin(["banned", "locked"])
d["is_surv"] = d["outcome"] == "survived"
pay = {"virtual_card": "чужие деньги", "reseller": "чужие деньги", "gift": "чужие деньги",
       "own_card_foreign": "своя карта", "own_card_local": "своя карта", "app_store": "App Store / Google Play"}
d["pay_group"] = d["payment_method"].map(pay).fillna("unknown")
ip = {"datacenter_vps": "свой VPS", "commercial_vpn": "общий VPN", "residential_vpn": "резидентный / домашний",
      "home_native": "резидентный / домашний", "mobile": "резидентный / домашний", "corporate": "корпоративный"}
d["ip_group"] = d["access_ip"].map(ip).fillna("unknown")
d["plan_group"] = d["plan"].replace({"max5": "Max 5x", "max20": "Max 20x", "pro": "Pro", "free": "Free",
                                     "team": "Team/Enterprise", "enterprise": "Team/Enterprise", "api": "API"})
d["age_group"] = pd.cut(d["age"], [-0.1, 1, 6, 12, 1000], labels=["до месяца", "1–6 мес", "6–12 мес", "больше года"]).astype(str)
d.loc[d["age"].isna(), "age_group"] = "unknown"


def fisher(a, b, c, e):
    """Двусторонний точный тест Фишера для [[a, b], [c, e]]."""
    n, r1, c1 = a + b + c + e, a + b, a + c
    p0 = comb(c1, a) * comb(n - c1, r1 - a) / comb(n, r1)
    p = 0.0
    for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1):
        px = comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
        if px <= p0 * (1 + 1e-9):
            p += px
    return min(p, 1.0)


def md(df):
    df = df.reset_index()
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)] +
                     ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])


out = ["# Кого банят: расчёт по группам\n",
       f"Кейсов: {len(d)}. Группа «РФ» — пользователь из России по тексту или кейс с русскоязычной площадки; "
       "«Китай и Гонконг» — по тексту или с linux.do/V2EX; «мир» — остальное (Reddit, GitHub, HN, X, регион обычно не назван).\n",
       "Доля банов = забаненные / (забаненные + выжившие) среди историй, где признак назван. Это доля среди рассказчиков, "
       "а не вероятность бана: выжившие пишут реже. Сравнивать можно строки внутри одной таблицы.\n"]

out.append("## Исходы по группам\n")
out.append(md(pd.crosstab(d["group"], d["outcome"], margins=True, margins_name="всего")))

for g in ["РФ", "Китай и Гонконг", "РФ + Китай и Гонконг", "мир"]:
    s = d[d["group"].isin(["РФ", "Китай и Гонконг"])] if g == "РФ + Китай и Гонконг" else d[d["group"] == g]
    s = s[s["is_ban"] | s["is_surv"]]
    out.append(f"\n## {g}: забаненные и выжившие (n = {len(s)})\n")
    for f, label in [("plan_group", "тариф"), ("pay_group", "оплата"), ("ip_group", "выход в интернет"),
                     ("ip_stable", "IP стабилен"), ("age_group", "возраст аккаунта"), ("automation", "автоматизация")]:
        k = s[s[f] != "unknown"]
        if len(k) < 8:
            continue
        t = k.groupby(f).agg(забанены=("is_ban", "sum"), выжили=("is_surv", "sum"))
        t["всего"] = t.sum(axis=1)
        t["доля банов, %"] = (t["забанены"] / t["всего"] * 100).round(0).astype(int)
        # Фишер: строка против всех остальных
        tb, ts = t["забанены"].sum(), t["выжили"].sum()
        t["p (против остальных)"] = [f"{fisher(int(r.забанены), int(r.выжили), int(tb - r.забанены), int(ts - r.выжили)):.3f}"
                                     for r in t.itertuples()]
        t = t[t["всего"] >= 3].sort_values("доля банов, %", ascending=False)
        out.append(f"### {label} (известно в {len(k)} историях)\n")
        out.append(md(t))
        out.append("")

# мир: когда банят
w = d[(d["group"] == "мир") & d["is_ban"]]
wa = w[w["age_group"] != "unknown"]
out.append(f"\n## Мир: возраст аккаунта в момент бана (известен у {len(wa)} из {len(w)})\n")
out.append(md(wa["age_group"].value_counts().to_frame("n")))

# причины, которые называют сами (по notes), все группы
kw = {"возраст / «ребёнок» / Yoti": r"возраст|ребён|ребен|несовершеннолет|yoti|under.?18|child",
      "сразу после оплаты / апгрейда / смены карты": r"после оплат|сразу после|апгрейд|оплатил|смен\w* карт|продлил|через \d+ (?:мин|час)",
      "VPN / смена IP или страны / поездка": r"vpn|впн|смен\w* (?:ip|айпи|стран)|поездк|путешеств|прокси|tun",
      "несколько аккаунтов / одна карта на несколько": r"несколько аккаунт|втор\w* аккаунт|одна карта|\d+ аккаунт|мультиакк",
      "автоматизация / -p / сторонние клиенты / реверс-прокси": r"claude -p|-p\b|harness|opencode|openclaw|реверс|sub2api|api-прокси|автоматиз|скрипт|ci\b",
      "перекупщик / купленный аккаунт / гифт": r"перекуп|реселл|купленн|посредник|гифт|gift|taobao|淘宝",
      "темы запросов (кибер, медицина, Китай, Ascend)": r"ascend|huawei|кибер|эксплойт|медицин|тем\w* чат|содержан"}
out.append("\n## Что называют в историях (по пересказам, грубый подсчёт регулярками; один кейс может попасть в несколько строк)\n")
rows = []
for name, rx in kw.items():
    m = d["notes"].str.lower().str.contains(rx, regex=True)
    rows.append({"признак": name, **{g: int((m & (d["group"] == g)).sum()) for g in ["РФ", "Китай и Гонконг", "мир"]}})
out.append(md(pd.DataFrame(rows).set_index("признак")))

# возвраты
out.append("\n## Возвраты (забаненные с известным исходом возврата)\n")
r = d[d["is_ban"] & d["refund"].isin(["full", "partial", "none"])].copy()
r["half"] = r["date"].dt.year.astype("Int64").astype(str) + "-" + ((r["date"].dt.quarter > 2).map({True: "H2", False: "H1"}))
out.append(md(pd.crosstab([r["group"], r["half"]], r["refund"])))
rr = d[(d["group"] == "РФ") & d["is_ban"] & d["refund"].isin(["full", "partial", "none"])]
out.append("\n### РФ по месяцам\n")
out.append(md(pd.crosstab(rr["date"].dt.to_period("M").astype(str), rr["refund"])))

# апелляции
out.append("\n## Апелляции по группам\n")
a = d[d["appeal"].isin(["accepted", "rejected", "pending"])]
out.append(md(pd.crosstab(a["group"], a["appeal"])))
reg = d[d["notes"].str.lower().str.contains(r"supported|регион|стран|country|countries")]
out.append(f"\nИстории, где в письме или пересказе упомянут регион/страна: {len(reg)}; апелляция принята: "
           f"{int((reg['appeal'] == 'accepted').sum())}, отклонена: {int((reg['appeal'] == 'rejected').sum())}.\n")

# новые аккаунты
out.append("\n## Новый аккаунт после бана\n")
n = d[d["new_account"].isin(["alive", "banned_fast", "kyc_required"])]
out.append(md(pd.crosstab(n["group"], n["new_account"])))

# волны: кейсы банов по неделям и группам
ban = d[d["is_ban"] & d["date"].notna() & (d["date"] >= "2025-01-01")]
wk = ban.groupby([pd.Grouper(key="date", freq="W-MON"), "group"]).size().unstack(fill_value=0)
top = wk.sum(axis=1).sort_values(ascending=False).head(12)
out.append("\n## Недели с наибольшим числом историй банов\n")
out.append(md(wk.loc[top.index].sort_index()))
# помесячный график без Telegram-чатов: их выгружали только с сентября 2026, месяцы иначе несравнимы
ban_m = ban[~ban["file"].isin(["wave_tg_a.csv", "wave_tg_b.csv"])] if "file" in ban else ban
mo = ban_m.groupby([pd.Grouper(key="date", freq="MS"), "group"]).size().unstack(fill_value=0)
ax = mo.plot(kind="bar", stacked=True, figsize=(11, 4.5), color={"РФ": "#c0392b", "Китай и Гонконг": "#e67e22", "мир": "#7f8c8d"})
ax.set_xticklabels([x.strftime("%Y-%m") for x in mo.index], rotation=60)
ax.set_ylabel("историй банов")
ax.set_xlabel("")
ax.legend(title=None)
ax.set_title(f"Истории банов Claude по месяцам: {len(ban_m)} историй, без Telegram-чатов")
plt.tight_layout()
plt.savefig(HERE / "results" / "bans_by_month_groups.png", dpi=150)
plt.close()

(HERE / "results" / "groups.md").write_text("\n".join(out), encoding="utf-8")
print("groups.md written")
