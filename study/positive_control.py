"""Post hoc disjoint separable-pair diagnostic with a balanced target for every pair."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from prepare_cases import ROOT,read,fields,build,SEED,write_json,SYSTEM

def cases():
    _,key=build(SEED)
    used={k['run_'+s] for k in key for s in 'AB'};rng=np.random.default_rng(481129)
    allrows=[r for r in read() if r['run'] not in used];prompts=[];keys=[]
    for task in sorted({r['task'] for r in allrows},key=int):
        rows=[r for r in allrows if r['task']==task];buckets=defaultdict(lambda:defaultdict(list))
        for i in rng.permutation(len(rows)):
            r=rows[i];a,k=fields(r);buckets[a][k].append(r)
        pairs=[]
        for groups in buckets.values():
            while True:
                remaining=sorted((k for k in groups if groups[k]),key=lambda k:-len(groups[k]))
                if len(remaining)<2:break
                pairs.append((groups[remaining[0]].pop(),groups[remaining[1]].pop()))
        for i in rng.permutation(len(pairs))[:16]:
            a,b=pairs[i]
            if rng.integers(0,2):a,b=b,a
            acc,ka=fields(a);_,kb=fields(b);number=len(keys)//2+1
            for j,target in enumerate(rng.permutation(['A','B'])):
                pair=f'D{number:03d}-{j+1}';kt=ka if target=='A' else kb
                user=(f'Catalog A: accuracy {acc}%, kappa {ka}.\nCatalog B: accuracy {acc}%, kappa {kb}.\nRecovered export: accuracy {acc}%, kappa {kt}.\nWhich catalog entry produced the export? A or B?')
                prompts.append(dict(pair=pair,condition='positive_control',user=user))
                keys.append(dict(pair=pair,task=task,run_A=a['run'],run_B=b['run'],target=str(target)))
    return prompts,keys

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--dir',type=Path,default=ROOT/'diagnostic');ap.add_argument('--key-dir',type=Path,required=True);ap.add_argument('--scores',type=Path,nargs='+');a=ap.parse_args()
    if a.key_dir.resolve()==a.dir.resolve() or a.dir.resolve() in a.key_dir.resolve().parents: raise ValueError('Separate prompts from keys')
    prompts,keys=cases();a.dir.mkdir(parents=True,exist_ok=True);a.key_dir.mkdir(parents=True,exist_ok=True)
    write_json(a.dir/'prompts.json',dict(system=SYSTEM,cases=prompts));write_json(a.key_dir/'diagnostic.json',keys)
    if a.scores:
        with (a.dir/'by_task.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['method','task','prompts','correct','selected_A'])
            ys={k['pair']:k for k in keys}
            agents={'First compatible':{k['pair']:k['target'] for k in keys},'Always A':{k['pair']:'A' for k in keys}}
            for filename in a.scores:
                with filename.open() as src:agents[json.loads(filename.with_suffix('.json').read_text())['model']]={r['pair']:r['selection'] for r in csv.DictReader(src)}
            for method,ans in agents.items():
                assert set(ans)==set(ys)
                for t in sorted({k['task'] for k in keys},key=int):
                    group=[k for k in keys if k['task']==t]
                    w.writerow([method,t,len(group),sum(ans[k['pair']]==k['target'] for k in group),sum(ans[k['pair']]=='A' for k in group)])
    print(len(keys)//2,'pairs')
