"""Assess rounded-score recovery when the set of compatible OpenML runs expands."""
import argparse
import csv
import random
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from statistics import mean, median, quantiles

ROOT = Path(__file__).resolve().parent
DELTAS = (('accuracy_1pp','1',None),('coarse_both','1','.1'),
          ('accuracy_0.1pp','.1',None),('fine_both','.1','.01'))
TOLERANCE = Decimal('0.02')

def load(path, old=False):
    records = []
    with path.open() as source:
        for row in csv.DictReader(source):
            accu = Decimal(row['predictive_accuracy']) * 100
            kappa = Decimal(row['kappa'])
            keys = []
            for name, step, kstep in DELTAS:
                key = (accu.quantize(Decimal(step), rounding=ROUND_HALF_EVEN),)
                if kstep:
                    key += (kappa.quantize(Decimal(kstep),rounding=ROUND_HALF_EVEN),)
                keys.append(key)
            records.append((int(row['task']),int(row['run']),int(row['flow']),Decimal(row['area_under_roc_curve']),
                            0 if old else int(row['offset']),tuple(keys)))
    return records

def envelopes(records, col):
    groups = {}
    for task, _, _, auc, _, keys in records:
        key = (task, keys[col])
        group = groups.get(key)
        if group is None:
            groups[key] = [auc, auc, 1]
        else:
            group[0] = min(group[0], auc)
            group[1] = max(group[1], auc)
            group[2] += 1
    return groups

def count(records, groups, col):
    covered = unique = 0
    for task, _, _, _, _, keys in records:
        lo,hi,n = groups[(task, keys[col])]
        covered += hi-lo <= TOLERANCE
        unique += n==1
    return covered,unique

def save(root, filename, rows):
    with (root/filename).open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--first',type=Path,default=ROOT/'catalog.csv')
    ap.add_argument('--later',type=Path,default=ROOT/'page_catalog.csv')
    ap.add_argument('--out',type=Path,default=ROOT)
    args=ap.parse_args()
    first=load(args.first,old=True)
    later=load(args.later)
    records=first+later
    assert len({r[1] for r in records})==len(records)==10752
    tasks=sorted({r[0] for r in first})
    bytask={t:[r for r in records if r[0]==t] for t in tasks}
    pages=sorted({r[4] for r in records})
    stats=[]; flows=[]
    for page in pages+['all']:
        page_records=[r for r in records if page=='all' or r[4]==page]
        for task in tasks:
            chunk=[r for r in page_records if r[0]==task]
            assert len(chunk)==(1536 if page=='all' else 384)
            c=Counter(r[2] for r in chunk)
            mode,mcount=c.most_common(1)[0]
            flows.append(dict(offset=page,task=task,n=len(chunk),flows=len(c),flow_2228=c[2228],mode=mode,mode_n=mcount))
        if page=='all':
            settings=[('same',page_records),('first-page reports',first)]
        else:
            settings=[('same',page_records)]
        for report_name,reports in settings:
            for col,(name,_,_) in enumerate(DELTAS):
                groups=envelopes(page_records,col)
                for task in tasks:
                    rset=[r for r in reports if r[0]==task]
                    covered,unique=count(rset,groups,col)
                    stats.append(dict(candidate_page=page,report_set=report_name,task=task,format=name,
                                      reported=len(rset),candidates=len(page_records)//len(tasks),
                                      guaranteed=covered,unique=unique))
    draws=[]
    for seed in range(21112026,21112226):
        rng=random.Random(seed)
        sample=[]
        for t in tasks:
            sample+=rng.sample(bytask[t],384)
        row={'seed':seed}
        for col,(name,_,_) in enumerate(DELTAS):
            row[name]=count(sample,envelopes(sample,col),col)[0]
        draws.append(row)
    save(args.out,'catalog_expansion.csv',stats)
    save(args.out,'page_flow_counts.csv',flows)
    save(args.out,'mixed_page_draws.csv',draws)
    for ref,outcome in [(0,'same'),(384,'same'),(1536,'same'),(3072,'same'),('all','first-page reports'),('all','same')]:
        print(ref,outcome,[(fmt,sum(r['guaranteed'] for r in stats if r['candidate_page']==ref and r['report_set']==outcome and r['format']==fmt))
                           for fmt,_,_ in DELTAS])
    for fmt,_,_ in DELTAS:
        vals=[r[fmt] for r in draws]
        print('mixed pages',fmt, 'median/min/max',median(vals),min(vals),max(vals))
    print('distinct flow counts and 2228',[(p,len({r[2] for r in records if p=='all' or r[4]==p}),
                    sum(r[2]==2228 for r in records if p=='all' or r[4]==p)) for p in pages+['all']])

if __name__=='__main__':
    main()
