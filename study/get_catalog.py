"""Fetch publicly reported OpenML run metrics, dropping accounts and all raw examples."""
import argparse
import csv
import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from decimal import Decimal

ROOT=Path(__file__).resolve().parent
TASKS=(3,6,12,23,28,31,37)
FUNCTIONS=('predictive_accuracy','kappa','area_under_roc_curve')
PREFIX='https://www.openml.org/api/v1/json/evaluation/list/task'
LIMIT=384

def collect(pair, cache):
    task,metric=pair
    url=f'{PREFIX}/{task}/function/{metric}/limit/{LIMIT}'
    f=cache / f'{task}_{metric}_{LIMIT}.json' if cache else None
    if f and f.exists():
        raw=f.read_bytes()
    else:
        with urllib.request.urlopen(url,timeout=90) as resp:
            raw=resp.read()
        if f:
            f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
    data=json.loads(raw,parse_float=Decimal)['evaluations']['evaluation']
    vals={int(r['run_id']):{'task':task,'run':int(r['run_id']),'flow':int(r['flow_id']),'dataset':r['data_name'],'value':str(r['value'])} for r in data}
    return task,metric,vals,{'task':task,'metric':metric,'returned':len(data),'source':url,'source_sha256':hashlib.sha256(raw).hexdigest()}

def save(name,rows):
    with (ROOT/name).open('w',newline='') as out:
        wr=csv.DictWriter(out,fieldnames=list(rows[0]))
        wr.writeheader();wr.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path)
    opts=parser.parse_args()
    pieces={}
    meta=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for task,metric,vals,m in pool.map(lambda pair:collect(pair, opts.cache),((i,j) for i in TASKS for j in FUNCTIONS)):
            pieces[task,metric]=vals;meta.append(m)
    result=[]
    for t in TASKS:
        ids=set.intersection(*(set(pieces[t,m]) for m in FUNCTIONS))
        for i in sorted(ids):
            info=pieces[t,FUNCTIONS[0]][i]
            outcome={m:pieces[t,m][i]['value'] for m in FUNCTIONS}
            if any(not Decimal(v).is_finite() for v in outcome.values()):continue
            if not (0<=Decimal(outcome['predictive_accuracy'])<=1 and 0<=Decimal(outcome['area_under_roc_curve'])<=1 and -1<=Decimal(outcome['kappa'])<=1):continue
            result.append({k:info[k] for k in ('task','dataset','run','flow')}|outcome)
    save('catalog.csv',result);save('api_sources.csv',meta)
    print({t:sum(r['task']==t for r in result) for t in TASKS})
if __name__=='__main__':main()
