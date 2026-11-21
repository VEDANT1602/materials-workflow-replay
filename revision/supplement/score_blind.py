"""Score frozen responder functions on sealed source specifications, without edits."""
import importlib.util
import json
from pathlib import Path
import numpy as np
from mask import assignments
from recover import datasets,all_specs,fit,matching,write

HERE=Path(__file__).resolve().parent

def run():
    public,keys=assignments()
    raw=datasets()
    rows=[]
    for file in sorted(HERE.glob("blind_response_*.py")):
        loader=importlib.util.spec_from_file_location(file.stem,file)
        module=importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        for blind,hidden in zip(public,keys):
            assert blind['id']==hidden['id']
            case=blind['id']
            x,y=raw[case[0]]
            grid=[fit(x,y,np.median(x),spec) for spec in all_specs()]
            group=matching(grid,blind['fields'])
            ground=matching(grid,hidden['spec'])[0]
            truth_flag='identified' if len({r['winner'] for r in group})==1 else 'uncertain'
            status='ok'
            guess=score1=score2=flag=completion=''
            try:
                guess,score1,score2,completion,flag=module.replay(x.copy(),y.copy(),case,dict(blind['fields']))
                scores=np.array([score1,score2])
                assert np.isfinite(scores).all() and guess in ('cubic','spline')
                assert all(completion.get(k)==v for k,v in blind['fields'].items())
                target=np.array([ground['cubic'],ground['spline']])
                flags=[guess==ground['winner'],bool(np.all(np.round(scores,8)==np.round(target,8))),
                       bool(np.max(abs(scores-target))<=.01*y.std()),flag==truth_flag,completion==hidden['spec']]
            except Exception as exc:
                status=type(exc).__name__+': '+str(exc)
                flags=[False]*5
            rows.append(dict(responder=file.stem,case=case,nfields=len(blind['fields']),status=status,
                             guess=guess,cubic=score1,spline=score2,source_winner=ground['winner'],
                             source_cubic=ground['cubic'],source_spline=ground['spline'],truth_flag=truth_flag,flag=flag,
                             selected_fields=json.dumps(completion,sort_keys=True),
                             winner_correct=int(flags[0]),scores_exact=int(flags[1]),scores_tol=int(flags[2]),
                             ambiguity_correct=int(flags[3]),fields_exact=int(flags[4])))
    if len(rows)!=24:
        raise ValueError("Exactly 12 cases from each of two frozen implementations expected")
    write("blind_scored.csv",rows)

if __name__=="__main__":
    run()
