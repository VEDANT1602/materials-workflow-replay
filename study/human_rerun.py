"""Build and score a future blinded human reanalysis of public prediction files."""
import argparse,csv,gzip,hashlib,json,secrets
from pathlib import Path
import numpy as np
from aggregate_predictions import read_arff, compute

def write_csv(file,rows):
    with file.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

PARTIAL='The archived endpoint was area under the ROC curve (AUC). Reconstruct its scalar value to six decimal places. Record your analysis decisions and executable code.'
FULL='The archived endpoint was area under the ROC curve (AUC). Pool all out-of-fold rows first, compute one-versus-rest AUC for each class with tied scores receiving half credit, and average by the observed class frequencies. Report six decimal places and your executable code.'
INSTRUCTIONS="""# Recompute a missing published AUC

Your coordinator supplies one form (X or Y) and eight CSV.GZ prediction files. Each file has a fold identifier, a ground-truth class, and columns of held-out scores for the indicated classes. These are outputs of public benchmark classifiers. Each form gives the retained metadata for its eight records. Follow the row-specific record literally, choose reasonable defaults when information is missing and record the choices. Work independently and only from this packet. Build your own executable calculation using the language or libraries of your choice. Do not refit classifiers. Return your eight values, code, dependency versions and notes through the coordinator's study channel. No source identifier or published target value is provided in this form.

The data are transformations of public OpenML benchmark run outputs on two public tasks. Labels and folds have been anonymised, record order changed and the original row identifiers removed. Attribution to OpenML and the contributing run uploaders is maintained in the coordinator's source manifest and should accompany any unblinded redistribution. Task sources: https://www.openml.org/t/3 and https://www.openml.org/t/28. OpenML usage terms: https://www.openml.org/terms.
"""
def prepare(rawdir,packet,private):
    if packet.resolve()==private.resolve() or packet.resolve() in private.resolve().parents:raise ValueError('Separate destinations')
    packet.mkdir(parents=True,exist_ok=True);private.mkdir(parents=True,exist_ok=True)
    if list(packet.iterdir()):raise ValueError('The packet directory should be empty')
    rng=np.random.default_rng(secrets.randbits(64));dataset=[];keys=[];forms={'X':[],'Y':[]}
    for f in sorted(rawdir.glob('*.arff')):
        info=json.loads(f.with_suffix('.json').read_text());raw=f.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==info['sha256']
        fold,labels,y,p=read_arff(raw)
        pooled=compute(labels,y,p)['class-frequency']
        assert round(pooled,6)==round(float(info['auc']),6)
        dataset.append((info,fold,labels,y,p))
    for task in sorted({m[0]['task'] for m in dataset}):
        rows=[r for r in dataset if r[0]['task']==task]
        if len(rows)!=4:raise ValueError('Use four distinct runs from each task')
        for info,fold,labels,y,p in rows:
            code=secrets.token_hex(3);order=rng.permutation(len(labels));class_alias={labels[k]:f'C{j}' for j,k in enumerate(order)}
            fold_alias=dict(zip(np.unique(fold),rng.permutation(np.unique(fold))))
            with gzip.open(packet/(code+'.csv.gz'),'wt',newline='') as stream:
                w=csv.writer(stream);w.writerow(['fold','true_class']+[f'score_C{j}' for j in range(len(labels))])
                for i in rng.permutation(len(y)):w.writerow([int(fold_alias[fold[i]]),class_alias[y[i]],*p[i,order]])
            for name in forms:
                complete=(name=='X')
                forms[name].append(dict(case=code,retained_workflow_notes=FULL if complete else PARTIAL,auc_six_decimals='',aggregation_used='',code_filename=''))
                keys.append(dict(form=name,case=code,task=task,run=info['run'],complete=complete,archived_auc=info['auc'],source=info['url'],source_sha256=info['sha256'],participant_sha256=hashlib.sha256((packet/(code+'.csv.gz')).read_bytes()).hexdigest()))
    for name,rows in forms.items():
        rng.shuffle(rows);write_csv(packet/f'form-{name}.csv',rows)
    write_csv(private/'rerun-key.csv',keys)
    (packet/'instructions.md').write_text(INSTRUCTIONS)

def score(form,key_file,response,dest):
    with key_file.open() as f:keys={r['case']:r for r in csv.DictReader(f) if r['form']==form}
    with response.open() as f:answers=list(csv.DictReader(f))
    if {r['case'] for r in answers}!=set(keys) or len(answers)!=len(keys):raise ValueError('Cases missing, extra or duplicated')
    out=[]
    for r in answers:
        ans=float(r['auc_six_decimals']);key=keys[r['case']]
        if not np.isfinite(ans) or not 0<=ans<=1 or not r['code_filename'].strip():raise ValueError('AUC and code filename required')
        miss=abs(ans-float(key['archived_auc']))
        out.append(dict(case=r['case'],task=key['task'],complete=key['complete'],absolute_error=miss,within_001=miss<=.01,rounded_to_six_matches=round(ans,6)==round(float(key['archived_auc']),6)))
    write_csv(dest,out)

if __name__=='__main__':
    ap=argparse.ArgumentParser();subs=ap.add_subparsers(dest='action',required=True)
    p=subs.add_parser('prepare');p.add_argument('--raw',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--private',type=Path,required=True)
    p=subs.add_parser('score');p.add_argument('--form',choices=['X','Y'],required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--response',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.action=='prepare':prepare(a.raw,a.packet,a.private)
    else:score(a.form,a.key,a.response,a.out)
