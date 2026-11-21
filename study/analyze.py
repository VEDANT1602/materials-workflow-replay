"""Score full-catalog recovery and paired, conditional model outputs at task level."""
import argparse
import csv
from collections import defaultdict
from decimal import Decimal
import json
from pathlib import Path
import numpy as np
from prepare_cases import ROOT, read, numeric_value, fields

def save(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def catalog_report():
    rows=read();out=[]
    for task in sorted({r['task'] for r in rows},key=int):
        rr=[r for r in rows if r['task']==task]
        for astep,kstep in [('1',None),('1','0.1'),('0.1',None),('0.1','0.01')]:
            groups=defaultdict(list)
            for r in rr:
                key=(numeric_value(Decimal(r['predictive_accuracy'])*100,astep),)
                if kstep:key+=(numeric_value(r['kappa'],kstep),)
                groups[key].append(r)
            widths=[];sizes=[];guaranteed=0;median_errors=[]
            for group in groups.values():
                vals=[Decimal(r['area_under_roc_curve']) for r in group]
                span=max(vals)-min(vals);sizes.extend([len(vals)]*len(vals));widths.extend([float(span)]*len(vals))
                guaranteed+=sum(span<=Decimal('.02') for _ in vals)
                x=np.array([float(v) for v in vals]);median_errors.extend(abs(x-np.median(x)))
            out.append(dict(task=task,dataset=rr[0]['dataset'],n=len(rr),accuracy_pp=astep,kappa_step=kstep or 'missing',unique=sum(s==1 for s in sizes),guaranteed_auc_001=guaranteed,median_auc_span=float(np.median(widths)),maximum_auc_span=max(widths),median_candidates=float(np.median(sizes)),mean_absolute_median_guess_error=float(np.mean(median_errors))))
    save('catalog_summary.csv',out)
    return out

def score(key_path,files):
    key=json.loads(key_path.read_text());by_pair={k['pair']:k for k in key};data=read();by_id={r['run']:r for r in data}
    agents={}
    for f in files:
        name=json.loads(f.with_suffix('.json').read_text())['model']
        with f.open() as src:agents[name]={(r['pair'],r['condition']):r['selection'] for r in csv.DictReader(src)}
        assert len(agents[name])==2*len(key)
    result=[]; details=[]
    for task in sorted({k['task'] for k in key},key=int):
        cases=[k for k in key if k['task']==task]
        for condition in ['accuracy','accuracy_kappa']:
            for method in [*agents,'Always A','First compatible','Uniform random']:
                scores=[];errors=[];left=[]
                for k in cases:
                    aa,bb=k['auc_A'],k['auc_B'];target=k['target'];true=k['auc_'+target]
                    if method=='Uniform random':pr=.5
                    elif method=='Always A':pr=1.
                    elif method=='First compatible':
                        term='run_'+target
                        pr=float(condition=='accuracy' or fields(by_id[k['run_A']])[1]==fields(by_id[k[term]])[1])
                    else:pr=float(agents[method][k['pair'],condition]=='A')
                    correct=pr if target=='A' else 1-pr
                    err=pr*abs(aa-true)+(1-pr)*abs(bb-true)
                    scores.append(correct);errors.append(err);left.append(pr)
                    details.append(dict(pair=k['pair'],task=task,condition=condition,method=method,target=target,prob_A=pr,correct=correct,absolute_auc_error=err,distinguishable=condition=='accuracy_kappa' and k['kappa_separates']))
                result.append(dict(task=task,dataset=cases[0]['dataset'],method=method,condition=condition,n=len(scores),separated=sum(k['kappa_separates'] for k in cases) if condition=='accuracy_kappa' else 0,correct=sum(scores),selected_A=sum(left),mean_absolute_auc_error=float(np.mean(errors))))
    save('trial_by_task.csv',result);save('trial_scored.csv',details)
    return result

def summarize(rows):
    by_method=defaultdict(lambda:defaultdict(dict))
    for r in rows:
        by_method[r['method']][r['task']][r['condition']]=r
    out=[]
    for name,taskdata in by_method.items():
        for cond in ('accuracy','accuracy_kappa'):
            cohort=[v[cond] for v in taskdata.values()]
            fractions=np.array([x['correct']/x['n'] for x in cohort]);errors=np.array([x['mean_absolute_auc_error'] for x in cohort])
            out.append(dict(method=name,condition=cond,n=sum(r['n'] for r in cohort),correct=sum(r['correct'] for r in cohort),macro_accuracy=fractions.mean(),macro_mae=errors.mean(),selected_A=sum(r['selected_A'] for r in cohort),separated=sum(r['separated'] for r in cohort),loto_low=min(np.delete(fractions,i).mean() for i in range(len(fractions))),loto_high=max(np.delete(fractions,i).mean() for i in range(len(fractions)))))
    save('trial_summary.csv',out)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--key',type=Path);p.add_argument('--responses',type=Path,nargs='+');a=p.parse_args()
    c=catalog_report()
    if a.key and a.responses:
        for r in summarize(score(a.key,a.responses)):print(r)
