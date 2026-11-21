"""Post hoc sensitivity to the frequency with which each OpenML flow is represented."""
from collections import Counter, defaultdict
from decimal import Decimal
from itertools import groupby
from statistics import mean
from analyze import save
from prepare_cases import read, numeric_value

def assess(records, accuracy_step, kappa_step):
    buckets=defaultdict(list)
    for r in records:
        signature=(numeric_value(Decimal(r['predictive_accuracy'])*100,accuracy_step),)
        if kappa_step:
            signature+=(numeric_value(r['kappa'],kappa_step),)
        buckets[signature].append(Decimal(r['area_under_roc_curve']))
    return sum(len(x) for x in buckets.values() if max(x)-min(x)<=Decimal('.02'))

def main():
    rows=read()
    most=Counter(r['flow'] for r in rows).most_common(1)[0][0]
    first=[min(group,key=lambda r:int(r['run'])) for _,group in groupby(sorted(rows,key=lambda r:(r['task'],r['flow'])),key=lambda r:(r['task'],r['flow']))]
    out=[]
    for rule,cohort in [('All',rows),('Omit most frequent flow',[r for r in rows if r['flow']!=most]),('Lowest run per task and flow',first)]:
        for t in sorted({r['task'] for r in cohort},key=int):
            group=[r for r in cohort if r['task']==t];a=assess(group,'1',None);b=assess(group,'1','.1');c=assess(group,'.1','.01')
            out.append(dict(selection=rule,task=t,n=len(group),coarse_accuracy=a,coarse_both=b,fine_both=c,coarse_kappa_gain=(b-a)/len(group),fine_both_over_coarse_accuracy=(c-a)/len(group)))
    save('flow_sensitivity.csv',out)
    for rule in dict.fromkeys(r['selection'] for r in out):
        subset=[r for r in out if r['selection']==rule]
        print(rule,sum(r['n'] for r in subset),mean(r['coarse_kappa_gain'] for r in subset),mean(r['fine_both_over_coarse_accuracy'] for r in subset))

if __name__=='__main__':main()
