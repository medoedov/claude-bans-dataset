"""Predeclared descriptive counts; default input contains no free-text responses."""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTCOMES = ('ban_history', 'no_problems', 'contradictory', 'other_problem', 'unknown')
EVENTS = ('no_problems', 'registration_refused', 'payment_refused', 'subscription_revoked',
          'ban', 'serial_bans', 'shadowban', 'other')
PAYMENTS = ('own_named_foreign', 'virtual_russian_service', 'virtual_foreign_service',
            'reseller', 'gift', 'partner', 'free', 'other')
# All column indices below are zero-based: paid columns 31..36 = Excel 32..37.
FIELDS = {
    'geography': (0, ['Россия', 'Другая страна', 'Другая страна СНГ']),
    'tenure': (7, ['Меньше месяца', '1–6 месяцев', '6–12 месяцев', 'Больше года']),
    'payment_change': (39, ['Использовал один и тот же', 'Менял по другим причинам',
                            'Менял (был отказ → попробовал другой)']),
    'vpn_mode': (42, ['Постоянно одна и та же страна, один провайдер',
                     'Меняю страны и провайдеров', 'Не использую вообще', 'Использую периодически']),
    'vpn_type': (43, ['Платный коммерческий', 'Свой VPS / собственный сервер',
                     'Не использую', 'Корпоративный', 'Бесплатный']),
}
CROSS = {
    51: ['Оба работают', 'Да, ChatGPT работает нормально, Claude — нет', 'Не пробовал на одном сетапе'],
    52: ['Не было бана в Claude', 'ChatGPT работал нормально', 'Не пользовался ChatGPT в тот период'],
    53: ['Нет, не подавал', 'Да, не получил ответа', 'Да, отказали', 'Да, и бан был отменён'],
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def validate_headers(actual, expected):
    if len(actual) != 61 or actual != expected:
        raise ValueError('Source headers differ from the audited 61-column schema')


def extract(path):
    import openpyxl  # Optional dependency: not required to rerun the public export.
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheets = book.worksheets
        if len(sheets) != 1:
            raise ValueError('Expected exactly one source sheet')
        raw = list(sheets[0].values)
    finally:
        book.close()
    headers = json.loads((BASE / 'headers.json').read_text(encoding='utf-8'))
    validate_headers(list(raw[0]), headers)
    selected, blank, duplicates = [], [], defaultdict(list)
    for row_id, row in enumerate(raw[1:], 2):
        if not any(v is not None and v != '' for v in row):
            blank.append(row_id)
            continue
        if len(row) != 61:
            raise ValueError(f'Wrong width at row {row_id}')
        duplicates[tuple(row)].append(row_id)  # Full raw equality, never publish raw values/hashes.
        item = {'row_id': row_id}
        for name, (index, allowed) in FIELDS.items():
            if row[index] is not None and row[index] not in allowed:
                raise ValueError(f'Unexpected closed value at row {row_id}, column {index + 1}')
            item[name] = row[index]
        for name, start, codes in [('events', 8, EVENTS), ('payments', 31, PAYMENTS)]:
            item[name] = []
            for offset, code in enumerate(codes):
                value = row[start + offset]
                if code != 'other' and value is not None and value != headers[start + offset].split(' / ', 1)[1]:
                    raise ValueError(f'Unexpected checkbox at row {row_id}, column {start + offset + 1}')
                if value is not None and value != '':
                    item[name].append(code)
        for index, allowed in CROSS.items():
            if row[index] is not None and row[index] not in allowed:
                raise ValueError(f'Unexpected crosscheck at row {row_id}, column {index + 1}')
        item['crosscheck'] = {
            'chat_says_no_claude_ban': row[52] == 'Не было бана в Claude',
            'chat_event_answer': row[52] in CROSS[52][1:],
            'chat_works_claude_not': row[51] == CROSS[51][1],
            'appeal_answer_present': row[53] is not None,
            'appeal_submitted': row[53] in CROSS[53][1:],
        }
        selected.append(item)
    return {'source_url': 'https://t.me/tevschannel/693',
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_excel_rows_including_header': len(raw), 'blank_rows': blank,
            'exact_raw_duplicate_groups': [ids for ids in duplicates.values() if len(ids) > 1],
            'rows': selected}


def outcome(row):
    events = set(row['events'])
    if 'no_problems' in events and events - {'no_problems'}:
        return 'contradictory'
    if events & {'ban', 'serial_bans'}:
        return 'ban_history'
    if 'no_problems' in events:
        return 'no_problems'
    return 'other_problem' if events else 'unknown'


def exclusions(row, require_mode=False):
    reasons = []
    if row['geography'] != 'Россия':
        reasons.append('not_russia')
    if outcome(row) not in ('ban_history', 'no_problems'):
        reasons.append('not_two_main_outcomes')
    if len(row['payments']) != 1 or row['payments'][0] not in PAYMENTS[:6]:
        reasons.append('not_exactly_one_defined_paid_method')
    if row['payment_change'] != 'Использовал один и тот же':
        reasons.append('payment_not_explicitly_unchanged')
    if row['vpn_type'] is None:
        reasons.append('missing_vpn_type')
    if require_mode and row['vpn_mode'] is None:
        reasons.append('missing_vpn_mode')
    return reasons


def summary(rows):
    ids = {key: [r['row_id'] for r in rows if outcome(r) == key] for key in OUTCOMES}
    return {'n': len(rows), 'counts': {key: len(value) for key, value in ids.items()}, 'ids': ids}


def cells(rows, strata=(), complete=True):
    groups = defaultdict(list)
    for row in rows:
        key = (tuple(row['payments']), row['vpn_type']) + tuple(row[x] for x in strata)
        groups[key].append(row)
    if complete and rows:
        for payment, network in itertools.product({tuple(r['payments']) for r in rows},
                                                 {r['vpn_type'] for r in rows}):
            groups[(payment, network)]
    return [dict(payments=list(key[0]), vpn_type=key[1],
                 **dict(zip(strata, key[2:])), **summary(group))
            for key, group in sorted(groups.items(), key=lambda kv: repr(kv[0]))]


def calculate(export):
    rows = export['rows']
    ru = [r for r in rows if r['geography'] == 'Россия']
    strict = [r for r in rows if not exclusions(r)]
    strict_mode = [r for r in rows if not exclusions(r, True)]
    omitted = {i for group in export['exact_raw_duplicate_groups'] for i in group[1:]}
    masks = {str(r['row_id']): exclusions(r) for r in rows}
    cross = {
        'ban_history_but_chat_says_no_ban': [r['row_id'] for r in rows if outcome(r) == 'ban_history' and r['crosscheck']['chat_says_no_claude_ban']],
        'no_problems_but_chat_event_answer': [r['row_id'] for r in rows if outcome(r) == 'no_problems' and r['crosscheck']['chat_event_answer']],
        'no_problems_but_chat_claude_not': [r['row_id'] for r in rows if outcome(r) == 'no_problems' and r['crosscheck']['chat_works_claude_not']],
        'no_problems_but_appeal_submitted': [r['row_id'] for r in rows if outcome(r) == 'no_problems' and r['crosscheck']['appeal_submitted']],
    }
    return {'source_url': export['source_url'], 'source_sha256': export['source_sha256'],
            'all': summary(rows), 'russia': summary(ru), 'other_geography': summary([r for r in rows if r not in ru]),
            'strict_one_unchanged_payment': summary(strict), 'strict_with_mode': summary(strict_mode),
            'raw_event_counts': dict(Counter(e for r in rows for e in r['events'])),
            'raw_ban_union_ids': [r['row_id'] for r in rows if set(r['events']) & {'ban', 'serial_bans'}],
            'other_event_review_ids': [r['row_id'] for r in rows if 'other' in r['events']],
            'crosscheck_flags': cross,
            'missing_closed_fields': {key: [r['row_id'] for r in rows if r[key] is None] for key in FIELDS},
            'blank_source_rows': export['blank_rows'], 'filled_service_rows': [],
            'service_row_check': 'All nonempty rows passed closed-option and checkbox validation.',
            'strict_exclusion_masks': masks,
            'excluded': summary([r for r in rows if masks[str(r['row_id'])]]),
            'exclusions_by_reason': {reason: summary([r for r in rows if reason in masks[str(r['row_id'])]])
                                     for reason in sorted({s for values in masks.values() for s in values})},
            'strict_mode_exclusion_masks': {str(r['row_id']): exclusions(r, True) for r in rows},
            'ru_payment_x_type': cells(ru), 'strict_payment_x_type': cells(strict),
            'ru_by_mode': cells(ru, ('vpn_mode',), False), 'strict_by_mode': cells(strict_mode, ('vpn_mode',), False),
            'ru_by_tenure': cells(ru, ('tenure',), False), 'strict_by_tenure': cells(strict, ('tenure',), False),
            'ru_any_problem': {'any_problem_ids': [r['row_id'] for r in ru if set(r['events']) - {'no_problems'}],
                               'cells': [dict(cell, any_problem_ids=[i for ids in cell['ids'].values() for i in ids
                                         if set(next(r['events'] for r in ru if r['row_id'] == i)) - {'no_problems'}])
                                         for cell in cells(ru)]},
            'exact_duplicate_sensitivity': {'groups': export['exact_raw_duplicate_groups'], 'omitted_ids': sorted(omitted),
                                           'all': summary([r for r in rows if r['row_id'] not in omitted]),
                                           'ru_payment_x_type': cells([r for r in ru if r['row_id'] not in omitted]),
                                           'strict_payment_x_type': cells([r for r in strict if r['row_id'] not in omitted])}}


def markdown(result):
    lines = ['# Опрос Тевса: описательные таблицы', '',
             'Единица — ответ анкеты; ID — строка Excel. Данные мая 2026. Каждая строка входит в одну ячейку точного набора оплат × типа VPN.',
             'Нулевые ячейки показаны в основных таблицах; срезы режима и стажа показывают все наблюдавшиеся ячейки. Полные ID и маски — results.json.',
             'Это не риск бана, рейтинг безопасности или причинный эффект. Тип/режим VPN мог измениться после бана; общий стаж не равен сроку связки.', '',
             '| Срез | n | ban_history | no_problems | contradictory | other_problem | unknown |', '|---|---:|---:|---:|---:|---:|---:|']
    for name in ('all', 'russia', 'other_geography', 'strict_one_unchanged_payment', 'strict_with_mode', 'excluded'):
        s = result[name]
        lines.append('| ' + ' | '.join(map(str, [name, s['n']] + [s['counts'][x] for x in OUTCOMES])) + ' |')
    for name in ('ru_payment_x_type', 'strict_payment_x_type', 'ru_by_mode', 'strict_by_mode', 'ru_by_tenure', 'strict_by_tenure'):
        lines += ['', '## ' + name, '', '| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |', '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
        for c in result[name]:
            ids = '; '.join(k + ': ' + ','.join(map(str, v)) for k, v in c['ids'].items() if v) or '—'
            values = [' + '.join(c['payments']) or '(не отмечено)', c['vpn_type'] or '(пропуск)', c.get('vpn_mode', c.get('tenure')) or '—', c['n']]
            lines.append('| ' + ' | '.join(map(str, values + [c['counts'][k] for k in OUTCOMES] + [ids])) + ' |')
    lines += ['', '## Проверки', '', 'Причины строгих исключений пересекаются:']
    for reason, s in result['exclusions_by_reason'].items():
        lines.append(f'- {reason}: {s["n"]}; исходы {s["counts"]}.')
    lines += ['', 'Точные дубли всей исходной строки: ' + json.dumps(result['exact_duplicate_sensitivity']['groups']) + '.',
              'Сверка ChatGPT/апелляций (не меняет основной исход): ' + json.dumps(result['crosscheck_flags'], ensure_ascii=False) + '.',
              '«Другое» в событиях, без публикации текста: ' + str(result['other_event_review_ids']) + '.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', type=Path, help='Locally extract original source.xlsx; never publish it')
    args = parser.parse_args()
    path = BASE / 'selected-responses.json'
    if args.extract:
        dump(path, extract(args.extract))
    result = calculate(json.loads(path.read_text(encoding='utf-8')))
    dump(BASE / 'results.json', result)
    (BASE / 'tables.md').write_text(markdown(result), encoding='utf-8')
    print(json.dumps({k: result[k]['counts'] for k in ('all', 'russia', 'strict_one_unchanged_payment')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
