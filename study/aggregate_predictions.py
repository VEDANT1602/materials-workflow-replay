"""Inspect aggregation choices against two public prediction files, without refitting."""
import argparse
import csv
import hashlib
import io
from pathlib import Path
import urllib.request
import numpy as np
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parent
FILES={'chess':(28,'https://openml.org/data/download/118/weka_generated_predictions7482092922181322979.arff'),
       'digits':(73,'https://openml.org/data/download/208/weka_generated_predictions7272255252095875325.arff')}

def read_arff(raw):
    header,data=raw.decode().split('@data',1)
    labels=[s.split()[1].split('.',1)[1] for s in header.splitlines() if s.startswith('@attribute confidence.')]
    records=list(csv.reader(io.StringIO(data.strip())))
    fold=np.array([int(r[1]) for r in records]);y=np.array([r[-1] for r in records]);p=np.array([[float(x) for x in r[3:-2]] for r in records])
    assert len(set(r[0] for r in records))==1 and len(fold)==len(set(r[2] for r in records))
    return fold,labels,y,p

def compute(labels,y,p):
    auc=[];counts=[]
    for i,k in enumerate(labels):
        pos=y==k;m=int(pos.sum());n=len(y)-m
        if not (n and m): raise ValueError('Undefined one-vs-rest AUC')
        r=rankdata(p[:,i],method='average')
        auc.append((r[pos].sum()-m*(m+1)/2)/(m*n));counts.append(m)
    return {'macro':float(np.mean(auc)),'class-frequency':float(np.average(auc,weights=counts))}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
    args.cache.mkdir(parents=True,exist_ok=True)
    source=[];out=[]
    with (ROOT/'catalog.csv').open() as f:archive={r['run']:float(r['area_under_roc_curve']) for r in csv.DictReader(f)}
    for name,(run,url) in FILES.items():
        file=args.cache/(name+'.arff')
        if not file.exists():
            with urllib.request.urlopen(url,timeout=90) as resp:file.write_bytes(resp.read())
        raw=file.read_bytes();fold,labels,y,p=read_arff(raw);unique=np.unique(fold)
        source.append({'run':run,'raw_file':url,'sha256':hashlib.sha256(raw).hexdigest(),'n':len(y),'folds':len(unique)})
        by_fold=[compute(labels,y[fold==i],p[fold==i]) for i in unique];pooled=compute(labels,y,p)
        counts=[np.sum(fold==i) for i in unique]
        for average in pooled:
            for pooling,auc in [('pooled predictions',pooled[average]),('equal-fold mean',np.mean([r[average] for r in by_fold])),('fold-size weighted',np.average([r[average] for r in by_fold],weights=counts))]:
                ref=archive[str(run)];out.append(dict(run=run,dataset=name,class_average=average,fold_method=pooling,reconstructed_auc=auc,archived_auc=ref,absolute_difference=abs(auc-ref)))
    for file,data in [('prediction_sources.csv',source),('aggregation_audit.csv',out)]:
        with (ROOT/file).open('w',newline='') as out:
            w=csv.DictWriter(out,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
if __name__=='__main__':main()
