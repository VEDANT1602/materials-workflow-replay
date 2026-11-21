"""Verify primary and diagnostic keys, grouped estimates and predictions from saved files."""
import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from prepare_cases import build, SEED
from positive_control import cases

ROOT=Path(__file__).resolve().parent
def records(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))

def digest(pair):return hashlib.sha256((json.dumps(pair,indent=2)+'\n').encode()).hexdigest()

def verify():
    catalog=records('catalog.csv')
    assert len({(r['task'],r['run']) for r in catalog})==len(catalog)==2688
    assert len({r['flow'] for r in catalog})==180
    recomputed={}
    for acc,kap in [('1',None),('1','.1'),('.1',None),('.1','.01')]:
        sets=defaultdict(list)
        for row in catalog:
            key=[row['task'],(Decimal(row['predictive_accuracy'])*100).quantize(Decimal(acc))]
            if kap:key.append(Decimal(row['kappa']).quantize(Decimal(kap)))
            sets[tuple(key)].append(Decimal(row['area_under_roc_curve']))
        recomputed[acc,kap]=(sum(len(vals) for vals in sets.values() if max(vals)-min(vals)<=Decimal('.02')),sum(len(vals) for vals in sets.values() if len(vals)==1))
    assert list(recomputed.values())==[(1066,30),(1110,43),(1721,208),(2216,318)]
    p,k=build(SEED);q,l=cases()
    assert digest(k)=='64ecbd24c0514d02bc5bd961d7ec9709a927e4ada724583843d7dc72715f9f13'
    assert (ROOT/'prompts/prompt_cases.json').read_bytes()==(json.dumps(json.loads((ROOT/'prompts/prompt_cases.json').read_text()),indent=2)+'\n').encode()
    assert p==json.loads((ROOT/'prompts/prompt_cases.json').read_text())['cases']
    assert q==json.loads((ROOT/'diagnostic/prompts.json').read_text())['cases']
    ids={v['run_'+s] for v in k for s in 'AB'}
    jds={v['run_'+s] for v in l for s in 'AB'}
    assert len(ids)==224 and len(jds)==98 and not ids&jds
    assert all(sum(r['target']=='A' for r in k if r['task']==t)==8 for t in {r['task'] for r in k})
    assert sum('-0.0' in x['user'] for x in p)==0 and sum('-0.0' in x['user'] for x in q)==4
    summary={};original={r['run']:r for r in catalog}
    for prefix,prompts,keys in [('',p,k),('diagnostic/',q,l)]:
        by_pair={x['pair']:x for x in keys};expected=len(prompts)
        for method in ('smol','qwen'):
            rows=records(prefix+method+'_answers.csv')
            assert len(rows)==expected
            provenance=json.loads((ROOT/(prefix+method+'_answers.json')).read_text())
            assert provenance['number_of_responses']==len(rows)
            assert provenance['distinct_prompts']==len(set(r['user'] for r in prompts))
            summary[prefix+method]=[0,0]
            system=json.loads((ROOT/('diagnostic/prompts.json' if prefix else 'prompts/prompt_cases.json')).read_text())['system']
            logit_by_hash={}
            for trial,prompt in zip(rows,prompts):
                text='<|im_start|>system\n'+system+'<|im_end|>\n<|im_start|>user\n'+prompt['user']+'<|im_end|>\n<|im_start|>assistant\n'
                sig=hashlib.sha256(text.encode()).hexdigest()
                assert sig==trial['prompt_sha256'] and trial['pair']==prompt['pair'] and trial['condition']==prompt['condition']
                scores=(float(trial['logit_A']),float(trial['logit_B']))
                assert trial['selection']==('A' if scores[0]>=scores[1] else 'B')
                if sig in logit_by_hash:assert scores==logit_by_hash[sig]
                logit_by_hash[sig]=scores
                summary[prefix+method][0]+=int(trial['selection']==by_pair[trial['pair']]['target'])
                summary[prefix+method][1]+=int(trial['selection']=='A')
        for v in keys:
            a,b=(original[v['run_'+s]] for s in 'AB')
            sa,sb=(str(Decimal(r['kappa']).quantize(Decimal('.1'))) for r in [a,b])
            assert (sa!=sb)==(Decimal(sa)!=Decimal(sb))
    assert summary=={'smol':[112,224],'qwen':[112,224],'diagnostic/smol':[49,98],'diagnostic/qwen':[59,88]}
    ar=records('aggregation_audit.csv')
    assert sum(float(r['absolute_difference'])<=0.0000005 and r['class_average']=='class-frequency' and r['fold_method']=='pooled predictions' for r in ar)==2
    packet=ROOT/'human-participant'
    for file in packet.rglob('*.csv'):
        with file.open() as f:rows=list(csv.DictReader(f))
        assert not any('run_id' in r or 'target' in r or 'source' in r or 'archived_auc' in r for r in rows)
        assert not rows, 'Public follow-up forms should be blank templates'
    print('Verified catalog counts, hidden-key hash, disjoint model cases, numeric zero treatment, 644 responses including repeated texts, two source reconstructions and blank human forms.')

if __name__=='__main__':verify()
