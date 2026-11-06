"""Reproduce descriptive tables for v2 with Python's standard library."""
import csv
import json
from collections import Counter
from pathlib import Path


def analyze(folder):
    with (folder / "cases.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    new = [r for r in rows if r["cohort"] == "addition"]
    updated = [r for r in rows if r["cohort"] == "legacy_followup"]
    strict = [r for r in new if r["product"] == "consumer" and r["evidence_class"] == "firsthand"]
    result = {"all_rows": len(rows), "additions": len(new), "legacy_followups": len(updated),
              "new_by_outcome": dict(sorted(Counter(r["outcome"] for r in new).items())),
              "new_by_source": dict(sorted(Counter(r["source"] for r in new).items())),
              "new_by_product": dict(sorted(Counter(r["product"] for r in new).items())),
              "new_by_visibility": dict(sorted(Counter(r["evidence_visibility"] for r in new).items())),
              "strict_consumer_firsthand": len(strict),
              "strict_by_outcome": dict(sorted(Counter(r["outcome"] for r in strict).items())),
              "strict_missing_fields": {k: sum(r[k] in {"", "unknown"} for r in strict) for k in ("usage", "plan", "kyc", "user_region", "payment_method", "ip_stable")}}
    (folder / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Состав расширения", "", f"Всего строк: {len(rows)}. Добавлено: {len(new)}. Старых аккаунтов с продолжением: {len(updated)}.", "",
             "Это состав найденных свидетельств, не вероятность бана. Старые и новые строки собраны по разным правилам; сравнение долей между волнами и причинный эффект признаков не рассчитываются.", ""]
    for title, key in (("Новые записи: исход", "new_by_outcome"), ("Новые записи: источник", "new_by_source"),
                       ("Новые записи: продукт", "new_by_product"), ("Новые записи: доступность источника", "new_by_visibility"),
                       ("Подвыборка consumer от первого лица: исход", "strict_by_outcome"),
                       ("Пропуски в подвыборке consumer от первого лица", "strict_missing_fields")):
        lines.extend([f"## {title}", "", "| Категория | Число |", "|---|---:|"])
        lines.extend(f"| {k} | {v} |" for k, v in result[key].items())
        lines.append("")
    lines.extend(["`active` — доступ на последнюю подтверждённую дату, не обещание сохранения доступа после неё. `kyc_prompt` и `locked` не смешаны с подтверждённым баном. Связанные аккаунты не независимые люди.", "",
                  "Пропуски не означают отсутствие признака. Legacy heavy и более подробные новые сведения о расходе не образуют сопоставимого измерения. Успешный KYC и доступ после него отражены разными событиями.", ""])
    (folder / "results.md").write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    print(json.dumps(analyze(parser.parse_args().folder), ensure_ascii=False))
