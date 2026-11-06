"""Extract public seller records without executing JS; reproduce notification statistics.

Run from any directory. Input and output are alongside this script. No network access.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
CHINA = timezone(timedelta(hours=8))
HORIZONS = (24, 48, 168, 336)


def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def extract(html):
    scripts = [s.get_text() for s in BeautifulSoup(html, "html.parser").find_all("script")]
    candidates = [s for s in scripts if 'generatedAt:' in s and 'accounts:' in s]
    if len(candidates) != 1:
        raise ValueError("Expected one data script")
    script = candidates[0]
    metadata = re.search(r'generatedAt:("[^"]+"),firstDate:("[^"]+"),minAtRisk:(\d+),minPlanAccounts:(\d+),delivered:(\d+),banned:(\d+)', script)
    if metadata is None:
        raise ValueError("Missing snapshot metadata")
    generated, first, min_risk, min_plan, delivered, banned = metadata.groups()
    meta = dict(generated_at=json.loads(generated), first_date=json.loads(first),
                min_at_risk=int(min_risk), min_plan_accounts=int(min_plan),
                delivered=int(delivered), banned=int(banned))
    pattern = r'\{no:(\d+),planLabel:("(?:[^"\\]|\\.)*"),deliveredHour:("[^"]+"),lifespanMinutes:(null|\d+),bannedDate:(null|"[^"]+")\}'
    rows = []
    for no, plan, delivered_at, lifespan, banned_date in re.findall(pattern, script):
        row = dict(no=int(no), plan=json.loads(plan), delivered_at=json.loads(delivered_at),
                   lifespan_minutes=json.loads(lifespan), banned_date=json.loads(banned_date))
        age = (dt(meta['generated_at']) - dt(row['delivered_at'])).total_seconds() / 3600
        event = row['lifespan_minutes'] is not None
        duration = row['lifespan_minutes'] / 60 if event else age
        if (event != (row['banned_date'] is not None)) or not 0 <= duration <= age:
            raise ValueError(f"Invalid chronology/status: {no}")
        date_matches = True
        if event:
            stamp = dt(row['delivered_at']) + timedelta(hours=duration)
            date_matches = stamp.astimezone(CHINA).date().isoformat() == row['banned_date']
            if not date_matches and (stamp + timedelta(hours=1)).astimezone(CHINA).date().isoformat() != row['banned_date']:
                raise ValueError(f"Ban date differs by more than delivery rounding: {no}")
        row.update(age_hours=age, duration_hours=duration, event=event,
                   ban_date_matches_duration=date_matches,
                   delivery_date=dt(row['delivered_at']).astimezone(CHINA).date().isoformat())
        rows.append(row)
    if len(rows) != meta['delivered'] or len({r['no'] for r in rows}) != len(rows):
        raise ValueError("Account count or uniqueness mismatch")
    if sum(r['event'] for r in rows) != meta['banned']:
        raise ValueError("Ban count mismatch")
    curve_block = re.search(r'curve:\$R\[\d+\]=\[(.*?)\],', script)
    if not curve_block:
        raise ValueError("Missing source KM curve")
    curve = [(float(h), float(p)) for h, p in re.findall(r'\{hours:([\d.]+),pct:([\d.]+)\}', curve_block[1])]
    return meta, rows, curve


def km_curve(observations):
    """(duration, event) pairs; events precede censoring at the same time."""
    events = Counter(t for t, event in observations if event)
    survival = 1.0
    curve = []
    for time, deaths in sorted(events.items()):
        at_risk = sum(t >= time for t, _ in observations)
        survival *= (at_risk - deaths) / at_risk
        curve.append(dict(hours=time, at_risk=at_risk, events=deaths, survival=survival))
    return curve


def survival_at(curve, horizon):
    return next((r['survival'] for r in reversed(curve) if r['hours'] <= horizon), 1.0)


def summarize(rows, horizon, shift=0):
    observations = [(max(0, r['duration_hours'] - shift), r['event']) for r in rows]
    curve = km_curve(observations)
    at_risk = sum(t >= horizon for t, _ in observations)
    eligible = [r for r in rows if r['age_hours'] - shift >= horizon]
    fixed_events = sum(r['event'] and max(0, r['duration_hours'] - shift) <= horizon for r in eligible)
    return dict(n=len(rows), horizon_hours=horizon, start_shift_hours=shift,
                events_by_horizon=sum(event and t <= horizon for t, event in observations),
                censored_before_horizon=sum(not event and t < horizon for t, event in observations),
                at_risk=at_risk, km_survival=survival_at(curve, horizon) if at_risk >= 10 else None,
                mature_n=len(eligible), mature_events=fixed_events,
                mature_fraction=fixed_events / len(eligible) if eligible else None)


def main():
    raw = (ROOT / 'meiguo.html').read_bytes()
    meta, rows, source_curve = extract(raw.decode('utf-8'))
    meta.update(source_url='https://meiguo.app/claude-ban-stats', sha256=hashlib.sha256(raw).hexdigest(),
                outcome='first_registered_ban_notification', timezone='UTC+8',
                observation_assumption='all notifications remain observed through generated_at')
    meta['ban_date_discrepancies_within_one_hour'] = [r['no'] for r in rows if not r['ban_date_matches_duration']]
    curve = km_curve([(r['duration_hours'], r['event']) for r in rows])
    # Source rounds hours and percentages, and emits tied events separately.
    # Compare the last source point at each rounded time with our last point there.
    own_rounded = {round(r['hours'], 1): round(r['survival'] * 100, 1) for r in curve}
    source_rounded = dict(source_curve)
    mismatches = {str(h): [p, own_rounded[h]] for h, p in source_rounded.items()
                  if h in own_rounded and abs(p - own_rounded[h]) > 0.11}
    shared_times = len(set(source_rounded) & set(own_rounded))
    meta['source_curve_comparison'] = dict(shared_rounded_times=shared_times, mismatches=mismatches)
    if not shared_times or mismatches:
        raise ValueError(f"Source curve differs: {meta['source_curve_comparison']}")
    groups = {'all': rows,
              'delivered_before_2026-10-29': [r for r in rows if r['delivery_date'] < '2026-10-29'],
              'delivered_from_2026-10-29': [r for r in rows if r['delivery_date'] >= '2026-10-29']}
    groups.update({f'current_plan_{p}': [r for r in rows if r['plan'] == p]
                   for p, count in Counter(r['plan'] for r in rows).items() if count >= 20})
    summary = [dict(group=name, **summarize(group, h, shift)) for name, group in groups.items()
               for h in HORIZONS for shift in (0, 1)]
    risk14 = summarize(rows, 336)['at_risk']
    meta['conditional_7_to_14_day_risk'] = (1 - survival_at(curve, 336) / survival_at(curve, 168)) if risk14 >= 10 else None
    meta['risk_set_day14'] = risk14
    meta['events_day7_to14'] = sum(r['event'] and 168 < r['duration_hours'] <= 336 for r in rows)
    meta['plan_counts'] = dict(Counter(r['plan'] for r in rows))
    for name, data in [('meiguo_accounts.csv', rows), ('meiguo_km.csv', curve), ('meiguo_horizons.csv', summary)]:
        with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    (ROOT / 'meiguo_summary.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=True))
    for entry in summary:
        if entry['start_shift_hours'] == 0 and entry['group'].startswith(('all', 'delivered_')):
            print(json.dumps(entry))


if __name__ == '__main__':
    main()
