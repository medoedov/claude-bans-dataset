"""Preserve a broad Russia-related review pool from public v2, not a citizen census."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT.parent / 'release' / 'v2'
RUSSIA_MENTION = re.compile(r'\b(?:РФ|RU|Russia|Russian)\b|росси[яйюи]', re.I)
RUSSIAN_LANGUAGE_CONTEXT = re.compile(r'русск(?:ое слово|ий язык|оязыч)', re.I)


def selection_reasons(case, details):
    reasons = []
    if case['group'].upper() == 'RU':
        reasons.append('source_group_ru')
    if case['user_region'].lower() == 'ru':
        reasons.append('location_ru_recorded')
    # Prior source audit found no document country in this account's testimony.
    if case['case_id'] != 'v2-0034' and any(str(d.get('document_country', '')).upper() == 'RU' for d in details):
        reasons.append('rf_document_recorded')
    text = case['notes'] + ' ' + case['usage_evidence']
    if case['case_id'] != 'v2-0034' and RUSSIA_MENTION.search(text):
        reasons.append('russia_text_mention')
    if RUSSIAN_LANGUAGE_CONTEXT.search(text):
        reasons.append('russian_language_context')
    return reasons


def select(cases, detail_rows, events, sources):
    ids = [c['case_id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate account IDs in input')
    details_by_id = defaultdict(list)
    for row in detail_rows:
        details_by_id[row['case_id']].append(json.loads(row['details_json']))
    reasons_by_id = {}
    for case in cases:
        reasons = selection_reasons(case, details_by_id[case['case_id']])
        if reasons:
            reasons_by_id[case['case_id']] = reasons
    # Account replacements need not repeat the owner's country in every note.
    graph = defaultdict(set)
    existing = set(ids)
    for case_id, details in details_by_id.items():
        for d in details:
            for other in d.get('related_case_ids', []):
                if case_id not in existing or other not in existing:
                    raise ValueError(f'Unknown related account: {case_id}, {other}')
                graph[case_id].add(other)
                graph[other].add(case_id)
    pending = list(reasons_by_id)
    while pending:
        current = pending.pop()
        for related in graph[current]:
            if related not in reasons_by_id:
                reasons_by_id[related] = ['related_to_russia_candidate']
                pending.append(related)
    membership = [dict(case_id=c['case_id'], reasons=';'.join(reasons_by_id[c['case_id']]),
                       status='candidate_not_citizenship_confirmation',
                       known_correction='RF document country unsupported; preserved input is not evidence' if c['case_id'] == 'v2-0034' else '',
                       cohort=c['cohort'], evidence_class=c['evidence_class'])
                  for c in cases if c['case_id'] in reasons_by_id]
    keep = {m['case_id'] for m in membership}
    return {'ru-candidates.csv': [r for r in cases if r['case_id'] in keep],
            'membership.csv': membership,
            'details.csv': [r for r in detail_rows if r['case_id'] in keep],
            'events.csv': [r for r in events if r['case_id'] in keep],
            'sources.csv': [r for r in sources if r['case_id'] in keep]}


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def main():
    inputs = {n: read_csv(INPUT / n) for n in ('cases.csv', 'details.csv', 'events.csv', 'sources.csv')}
    tables = select(*(inputs[n][1] for n in ('cases.csv', 'details.csv', 'events.csv', 'sources.csv')))
    for name, rows in tables.items():
        if name == 'membership.csv':
            fields = ['case_id', 'reasons', 'status', 'known_correction', 'cohort', 'evidence_class']
        else:
            fields = inputs['cases.csv' if name == 'ru-candidates.csv' else name][0]
        with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    cases = tables['ru-candidates.csv']
    summary = dict(input_rows=len(inputs['cases.csv'][1]), candidate_rows=len(cases),
                   basis_counts=dict(Counter(x for m in tables['membership.csv'] for x in m['reasons'].split(';'))),
                   by_cohort=dict(Counter(r['cohort'] for r in cases)),
                   outside_source_group_ru=[r['case_id'] for r in cases if r['group'].upper() != 'RU'],
                   table_rows={n: len(r) for n, r in tables.items()},
                   input_sha256={n: hashlib.sha256((INPUT / n).read_bytes()).hexdigest() for n in inputs},
                   interpretation='candidate pool; not confirmed Russian citizenship or representative risk sample')
    (ROOT / 'selection-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=True))


if __name__ == '__main__':
    main()
