"""Construct a balanced, anonymous, two-record linkage trial from actual OpenML runs."""
import argparse
import csv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SEED=21112026
SYSTEM='You are matching a damaged evaluation record to one of two catalog entries. Use only the fields shown. Select A or B. If both entries match the export equally well, choose your best guess. Reply with just the letter.'

def read():
    with (ROOT/'catalog.csv').open() as f:return list(csv.DictReader(f))

def value(number,step):
    return format(Decimal(number).quantize(Decimal(step),rounding=ROUND_HALF_EVEN),'f')

def numeric_value(number, step):
    rounded=Decimal(value(number,step))
    return rounded.copy_abs() if rounded.is_zero() else rounded

def fields(r):
    return (value(Decimal(r['predictive_accuracy'])*100,'1'),value(r['kappa'],'0.1'))

def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2)+'\n')

def build(seed):
    data=read();rng=np.random.default_rng(seed);prompts=[];keys=[];counter=0
    for task in sorted({r['task'] for r in data},key=int):
        rows=sorted([r for r in data if r['task']==task],key=lambda r:int(r['run']))
        buckets=defaultdict(list)
        for idx in rng.permutation(len(rows)):
            r=rows[idx];buckets[fields(r)[0]].append(r)
        pairs=[(group[i],group[i+1]) for group in buckets.values() for i in range(0,len(group)-1,2)]
        pairs=[pairs[i] for i in rng.permutation(len(pairs))[:16]]
        pairs=pairs[:len(pairs)//2*2]
        assignments=list(rng.permutation(['A','B']*(len(pairs)//2)))
        for (a,b),key in zip(pairs,assignments):
            counter+=1;ident=f'R{counter:03d}'
            true=a if key=='A' else b
            acc,kap=fields(true); ka=fields(a)[1];kb=fields(b)[1]
            keys.append(dict(pair=ident,task=task,dataset=true['dataset'],run_A=a['run'],run_B=b['run'],target=key,auc_A=float(a['area_under_roc_curve']),auc_B=float(b['area_under_roc_curve']),kappa_separates=ka!=kb))
            for cond,recorded in [('accuracy','not recorded'),('accuracy_kappa',kap)]:
                text=(f'Catalog A: accuracy {acc}%, kappa {ka}.\nCatalog B: accuracy {acc}%, kappa {kb}.\nRecovered export: accuracy {acc}%, kappa {recorded}.\nWhich catalog entry produced the export? A or B?')
                prompts.append(dict(pair=ident,condition=cond,user=text))
    return prompts,keys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=SEED)
    ap.add_argument('--key-dir',type=Path,required=True)
    ap.add_argument('--prompt-dir',type=Path,required=True)
    args=ap.parse_args()
    keydir=args.key_dir.resolve();promptdir=args.prompt_dir.resolve()
    if keydir==promptdir or promptdir in keydir.parents:
        raise ValueError('Keep the answer key outside the prompt packet.')
    keydir.mkdir(parents=True,exist_ok=True);promptdir.mkdir(parents=True,exist_ok=True)
    prompts,keys=build(args.seed)
    write_json(promptdir/'prompt_cases.json',dict(system=SYSTEM,cases=prompts))
    write_json(keydir/'scoring_key.json',keys)
    print('Key SHA-256',hashlib.sha256((keydir/'scoring_key.json').read_bytes()).hexdigest(),'pairs',len(keys))
if __name__=='__main__':main()
