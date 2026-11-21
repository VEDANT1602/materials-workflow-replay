"""Prepare anonymous, counterbalanced human lookup forms and a separate confidential key."""
import argparse
import csv
import hashlib
import json
import secrets
from collections import defaultdict
from pathlib import Path
import numpy as np
from prepare_cases import read, fields, build, SEED

INSTRUCTIONS = """# Link two historical catalog entries

Use the candidate entries and the recovered record printed on your assigned form. In each row select the original entry, A or B. If the two candidates cannot be distinguished, choose one, and mark the tie in the evidence column. In that column use either 'unique' or 'tie'. Fill in only the two blank columns. No search, archived records or model assistance are needed. Work independently. Keep only the single form assigned to you.

These are tasks prepared for a future study. No completed human answers are included. Return a completed form only through the channel designated by your study coordinator after receiving the study information.
"""

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def prepare(packet, private):
    if packet.resolve()==private.resolve() or packet.resolve() in private.resolve().parents:
        raise ValueError('The key must stay outside the participant folder')
    for folder in [packet,private]:
        folder.mkdir(exist_ok=True,parents=True)
        if list(folder.iterdir()):raise ValueError('Choose new empty output folders')
    seed=secrets.randbits(64);rng=np.random.default_rng(seed)
    _,model_key=build(SEED)
    used={k[f'run_{letter}'] for k in model_key for letter in 'AB'}
    from positive_control import cases
    _,diagnostic_keys=cases()
    used.update(k['run_'+s] for k in diagnostic_keys for s in 'AB')
    allrows=[r for r in read() if r['run'] not in used]
    forms={'X':[],'Y':[]};keys=[]
    for task in sorted({r['task'] for r in allrows},key=int):
        rows=[r for r in allrows if r['task']==task];bins=defaultdict(list)
        for i in rng.permutation(len(rows)):bins[fields(rows[i])[0]].append(rows[i])
        pairs=[(group[i],group[i+1]) for group in bins.values() for i in range(0,len(group)-1,2)]
        assignments=list(rng.permutation([('A',False),('A',True),('B',False),('B',True)]))
        for i,(target,show_x) in zip(rng.permutation(len(pairs))[:4],assignments):
            a,b=pairs[i];true=a if target=='A' else b
            acc,ka=fields(a);_,kb=fields(b);_,kt=fields(true);item=secrets.token_hex(4)
            for form in forms:
                reveal=bool(show_x) if form=='X' else not bool(show_x)
                forms[form].append(dict(item=item,accuracy_A_pct=acc,kappa_A=ka,accuracy_B_pct=acc,kappa_B=kb,export_accuracy_pct=acc,export_kappa=kt if reveal else 'not recorded',selection='',evidence=''))
                keys.append(dict(form=form,item=item,task=task,target=target,run_A=a['run'],run_B=b['run'],auc_A=a['area_under_roc_curve'],auc_B=b['area_under_roc_curve'],evidence='unique' if reveal and ka!=kb else 'tie'))
    for form,rows in forms.items():
        rng.shuffle(rows)
        write_csv(packet/f'form-{form}.csv',rows)
    (packet/'instructions.md').write_text(INSTRUCTIONS)
    write_csv(private/'human-key.csv',keys)
    (private/'generation.json').write_text(json.dumps(dict(seed=str(seed),key_sha256=hashlib.sha256((private/'human-key.csv').read_bytes()).hexdigest()),indent=2)+'\n')

def score(form_name, response, key):
    with key.open() as f:
        truth={r['item']:r for r in csv.DictReader(f) if r['form']==form_name}
    with response.open() as f:rows=list(csv.DictReader(f))
    if len(rows)!=len(truth) or set(r['item'] for r in rows)!=set(truth):
        raise ValueError('Incomplete case set or wrong key')
    result=[]
    for r in rows:
        k=truth[r['item']];choice=r['selection'].strip().upper()
        if choice not in ('A','B') or r['evidence'].strip().lower() not in ('unique','tie'):
            raise ValueError(f"Missing or invalid answer for {r['item']}")
        result.append(dict(item=r['item'],task=k['task'],recorded_kappa=r['export_kappa']!='not recorded',source_correct=choice==k['target'],evidence_correct=r['evidence'].strip().lower()==k['evidence'],absolute_auc_error=abs(float(k[f'auc_{choice}'])-float(k[f"auc_{k['target']}"]))))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();cmd=ap.add_subparsers(dest='mode',required=True)
    p=cmd.add_parser('prepare');p.add_argument('--packet',type=Path,required=True);p.add_argument('--private',type=Path,required=True)
    p=cmd.add_parser('score');p.add_argument('--form',choices=('X','Y'),required=True);p.add_argument('--response',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='prepare':prepare(args.packet,args.private)
    else:write_csv(args.out,score(args.form,args.response,args.key))
