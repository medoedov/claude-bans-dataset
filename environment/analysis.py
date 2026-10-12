"""Окружение, клиент и сочетание признаков: расчет для раздела статьи «Банят за отпечаток браузера и часовой пояс?»
и итогового раздела «Так за что банят». Вход — ../cases.csv и файлы этой папки. Выход — results.md.
Запуск: python environment/analysis.py"""
import json
from math import comb
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = []


def p(line=""):
    OUT.append(line)


def fisher(a, b, c, e):
    """Точный тест Фишера, двусторонний: a/b — бан/жив в первой группе, c/e — во второй."""
    n, r1, c1 = a + b + c + e, a + b, a + c
    pr = lambda x: comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9)))


def share(df):
    return f"{int(df.b.sum())} из {len(df)}" + (f" ({round(df.b.mean() * 100)}%)" if len(df) else "")


def test(x, y):
    return fisher(int(x.b.sum()), int((~x.b).sum()), int(y.b.sum()), int((~y.b).sum()))


# База — как в groups.py: россияне и китайцы, исход известен (бан, временная блокировка или жив)
d = pd.read_csv(HERE.parent / "cases.csv", dtype=str, keep_default_na=False)
s = d[d.outcome.isin(["banned", "locked", "survived"]) & d.group.isin(["RU", "CN"])].copy()
s["b"] = s.outcome != "survived"
p("# Окружение, клиент и сочетание признаков")
p()
p(f"База: россияне и китайцы с известным исходом — {len(s)} историй, забанены или временно заблокированы {share(s)}.")
p("Доля банов — среди рассказавших, сравнивать можно только строки между собой (см. method.md). p — точный тест Фишера.")

# 1. Клиент
cl = pd.read_csv(HERE / "clients.csv", dtype=str, keep_default_na=False)
rc = pd.read_csv(HERE / "clients_recheck150.csv", dtype=str, keep_default_na=False)
S = lambda v: frozenset(t for t in v.split(";") if t)
x = s.merge(cl, on="case_id")
x["S"] = x.clients.map(S)
x = x[x.S.map(len) > 0]
g = {
    "Только Claude Code": x[x.S.map(lambda v: v == {"cli"})],
    "Только браузер": x[x.S.map(lambda v: v == {"web"})],
    "С приложением Claude Desktop": x[x.S.map(lambda v: "desktop" in v)],
    "Без Claude Desktop": x[x.S.map(lambda v: "desktop" not in v)],
    "Любой Claude Code": x[x.S.map(lambda v: "cli" in v)],
    "Без Claude Code": x[x.S.map(lambda v: "cli" not in v)],
}
p()
p("## 1. Клиент: веб, Desktop, мобильное приложение, Claude Code")
p()
p(f"Клиент назван в {len(x)} историях из {len(s)}.")
p()
p("| Клиент | Все | Россияне | Китайцы |")
p("|---|---|---|---|")
for k, v in g.items():
    p(f"| {k} | {share(v)} | {share(v[v.group == 'RU'])} | {share(v[v.group == 'CN'])} |")
p()
p(f"- только Claude Code против только браузера: p = {test(g['Только Claude Code'], g['Только браузер']):.2f}")
p(f"- с Desktop против без Desktop: p = {test(g['С приложением Claude Desktop'], g['Без Claude Desktop']):.2f}")
p(f"- любой Claude Code против без Claude Code: p = {test(g['Любой Claude Code'], g['Без Claude Code']):.2f}")
j = cl.merge(rc, on="case_id", suffixes=("_m", "_r"))
named = sum((len(S(a)) > 0) == (len(S(b)) > 0) for a, b in zip(j.clients_m, j.clients_r))
same = sum(S(a) == S(b) for a, b in zip(j.clients_m, j.clients_r))
p()
p(f"Контрольная разметка {len(j)} случайных историй (`clients_recheck150.csv`): «клиент назван или нет» совпал в {named}, "
  f"набор клиентов совпал полностью в {same}.")

# 2. Сочетание признаков
age = pd.to_numeric(s.account_age_months, errors="coerce")
F = pd.DataFrame({
    "Max 20x": s.plan.map(lambda v: None if v == "unknown" else v == "max20"),
    "чужие деньги": s.payment_method.map(lambda v: None if v in ("unknown", "none") else v in ("virtual_card", "reseller", "gift")),
    "аккаунт младше месяца": age.map(lambda v: None if pd.isna(v) else v <= 1),
    "IP меняется": s.ip_stable.map(lambda v: None if v == "unknown" else v == "no"),
    "несколько аккаунтов": s.automation.map(lambda v: True if "multi_account" in v else (None if v == "unknown" else False)),
})
p()
p("## 2. Складываются ли признаки риска")
p()
p("Признаки: " + ", ".join(F.columns) + ". Считаются истории, где названо не меньше двух признаков из набора; "
  "признак, который не назван, не считается ни риском, ни его отсутствием.")


def combo(cols, k):
    f = F[cols]
    known = f.notna().sum(axis=1)
    risk = f.fillna(False).astype(int).sum(axis=1).clip(upper=2)
    y = s[known >= k].assign(r=risk[known >= k])
    r0, r1, r2 = (y[y.r == i] for i in (0, 1, 2))
    p(f"| {', '.join(cols)} | {len(y)} | {share(r0)} | {share(r1)} | {share(r2)} | {test(r0, r2):.2f} |")


p()
p("| Набор признаков | Историй | Ни одного | Один | Два и больше | p (0 против 2+) |")
p("|---|---|---|---|---|---|")
combo(list(F.columns), 2)
combo(["чужие деньги", "IP меняется", "несколько аккаунтов"], 2)
p()
for m, label in ((True, "на Max 20x"), (False, "не на Max 20x")):
    sub = s[F["Max 20x"] == m]
    f = F.loc[sub.index, ["чужие деньги", "аккаунт младше месяца", "IP меняется", "несколько аккаунтов"]]
    known = f.notna().sum(axis=1)
    risk = f.fillna(False).astype(int).sum(axis=1).clip(upper=2)
    y = sub[known >= 1].assign(r=risk[known >= 1])
    p(f"- {label}, по числу остальных признаков: " + "; ".join(f"{i}{'+' if i == 2 else ''} — {share(y[y.r == i])}" for i in (0, 1, 2)))

# 3. Тариф и волна 1 октября
ru = s[s.group == "RU"]
w = ru.wave == "2026-10-01"
used = s.usage.isin(["normal", "heavy"])
p()
p("## 3. Тариф и волна 1 октября")
p()
p("| Россияне | Max 20x | Pro и Max 5x | p |")
p("|---|---|---|---|")
for label, mask in (("волна 1 октября", w), ("вне волны 1 октября", ~w)):
    a_, c_ = ru[mask & (ru.plan == "max20")], ru[mask & ru.plan.isin(["pro", "max5"])]
    p(f"| {label} | {share(a_)} | {share(c_)} | {test(a_, c_):.4f} |")
for grp, label in (("RU", "работали с аккаунтом, россияне"), ("CN", "работали с аккаунтом, китайцы")):
    z = s[used & (s.group == grp)]
    a_, c_ = z[z.plan == "max20"], z[z.plan.isin(["pro", "max5"])]
    p(f"| {label} | {share(a_)} | {share(c_)} | {test(a_, c_):.4f} |")
p()
p("«Работали с аккаунтом» — usage normal или heavy, то есть не «только оплатил».")

# 4. Окружение в историях
e = pd.read_csv(HERE / "env.csv", dtype=str, keep_default_na=False)
agree = e[e.env_coder_a == e.env_coder_b]
described = agree[agree.env_coder_a != "not_described"]
z = s.merge(described[["case_id", "env_coder_a"]], on="case_id")
p()
p("## 4. Окружение в историях")
p()
p(f"Кандидатов, где упомянуты часовой пояс, язык, отпечаток, WebRTC или антидетект, — {len(e)}; две независимые разметки "
  f"совпали в {len(agree)}. Свое окружение описали {len(described)} человек из {len(s)}: для таблицы мало.")
p()
p("| Окружение | Забанены |")
p("|---|---|")
for k, label in (("antidetect", "антидетект"), ("matched", "выровнял часовой пояс, язык или WebRTC под IP"), ("mismatch", "рассинхрон с IP")):
    p(f"| {label} | {share(z[z.env_coder_a == k])} |")

# 5. Опрос ohaze со знаменателем
J = json.loads((HERE / "ohaze_board_2026-10-12.json").read_text(encoding="utf-8"))["data"]


def dims(block):
    for grp_ in block["groups"]:
        for dm in grp_["dims"]:
            yield dm["title"], {r["key"]: (r["c"]["banned"], r["c"]["restored"] + r["c"]["active"]) for r in dm["rows"]}


nd = dict(dims(J["network"]["all"]))
p()
p("## 5. Опрос ohaze (linux.do), снимок 12.10.2026")
p()
p(f"Одна анкета для живых и забаненных, {J['total']} анкет; окружение у {J['detect']} снято сайтом-детектором. "
  "Источник: https://claudeban.ohaze.workers.dev/board, обсуждение https://linux.do/t/topic/2982451. "
  "Бан — banned, жив — active + restored.")
p()
p("| Признак | Первая группа | Вторая группа | p |")
p("|---|---|---|---|")
for title, A, B, la, lb in (
    ("时区与出口", "same", "diff", "часовой пояс совпадает со страной IP", "не совпадает"),
    ("语言与格式与出口（中文环境、出口不在中文地区算不一致）", "same", "diff", "язык системы совпадает", "не совпадает"),
    ("泄露", "none", "webrtc", "нет утечек", "утечка WebRTC"),
    ("代理情况", "vps", "airport", "свой VPS", "общий VPN-сервис («аэропорт»)"),
):
    (a1, a2), (c1, c2) = nd[title][A], nd[title][B]
    p(f"| {la} / {lb} | {a1} из {a1 + a2} ({round(a1 / (a1 + a2) * 100)}%) | {c1} из {c1 + c2} ({round(c1 / (c1 + c2) * 100)}%) | {fisher(a1, a2, c1, c2):.3f} |")

(HERE / "results.md").write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n".join(OUT))
