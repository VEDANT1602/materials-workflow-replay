"""Retrieve disjoint OpenML evaluation pages for the finite-catalog sensitivity audit."""
import argparse
import csv
import hashlib
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from itertools import product
from pathlib import Path

TASKS = (3, 6, 12, 23, 28, 31, 37)
METRICS = ('predictive_accuracy', 'kappa', 'area_under_roc_curve')
OFFSETS = (384, 1536, 3072)
LIMIT = 384
ROOT = Path(__file__).resolve().parent
PREFIX = 'https://www.openml.org/api/v1/json'

def write_rows(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def fetch_url(url, cache_file):
    if cache_file.exists():
        return cache_file.read_bytes()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'OpenML-archived-score-study/1.0'})
            with urllib.request.urlopen(req, timeout=60) as res:
                data = res.read()
        except urllib.error.HTTPError as err:
            if err.code == 412:
                data = err.read()
            elif attempt < 2 and err.code in (429, 500, 502, 503, 504):
                time.sleep(2**attempt)
                continue
            else:
                raise
        except (TimeoutError, urllib.error.URLError, ConnectionError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)
            continue
        cache_file.write_bytes(data)
        return data

def collect(args, cache):
    task, metric, offset = args
    url = f'{PREFIX}/evaluation/list/task/{task}/function/{metric}/limit/{LIMIT}/offset/{offset}'
    raw = fetch_url(url, cache / f'{task}_{metric}_{offset}_{LIMIT}.json')
    obj = json.loads(raw, parse_float=Decimal)
    if 'error' in obj:
        if str(obj['error']['code']) != '542':
            raise ValueError((url, obj['error']))
        data = []
    else:
        data = obj['evaluations']['evaluation']
    cases = {}
    for row in data:
        assert int(row['task_id']) == task and row['function'] == metric
        value = Decimal(str(row['value']))
        assert value.is_finite() and (Decimal(-1) if metric == 'kappa' else 0) <= value <= 1
        run = int(row['run_id'])
        assert run not in cases
        cases[run] = (int(row['flow_id']), row['data_name'], str(value))
    meta = dict(task=task, metric=metric, offset=offset, limit=LIMIT, returned=len(cases),
                source=url, source_sha256=hashlib.sha256(raw).hexdigest())
    return (task, metric, offset), cases, meta

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', required=True, type=Path, help='non-distributed raw-response cache')
    args = p.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    requests = list(product(TASKS, METRICS, OFFSETS))
    rows, provenance, responses, joins = [], [], {}, []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for key, cases, meta in pool.map(lambda k: collect(k, args.cache), requests):
            responses[key] = cases
            provenance.append(meta)
    for task, offset in product(TASKS, OFFSETS):
        sets = [responses[task, metric, offset] for metric in METRICS]
        common = set.intersection(*(set(m) for m in sets))
        joins.append(dict(task=task, offset=offset, joined=len(common), union=len(set.union(*(set(m) for m in sets)))))
        for run in sorted(common):
            assert len({m[run][:2] for m in sets}) == 1
            flow, name = sets[0][run][:2]
            rows.append(dict(task=task, dataset=name, run=run, flow=flow, offset=offset,
                             **{metric:rs[run][2] for rs, metric in zip(sets,METRICS)}))
    assert len({r['run'] for r in rows}) == len(rows)
    write_rows(ROOT/'page_catalog.csv', rows)
    write_rows(ROOT/'page_sources.csv', provenance)
    write_rows(ROOT/'page_joins.csv', joins)
    for endpoint in ('task/44','evaluation/list/task/44/function/predictive_accuracy/limit/1'):
        raw = fetch_url(PREFIX+'/'+endpoint, args.cache/('failed_'+endpoint.replace('/','_')+'.json'))
        print(PREFIX+'/'+endpoint, raw[:180], hashlib.sha256(raw).hexdigest())
    print('joined later-page records',len(rows))

if __name__ == '__main__':
    main()
