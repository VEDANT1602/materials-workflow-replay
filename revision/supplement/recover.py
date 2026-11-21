"""Set-valued recovery and single-completion baseline on three measured datasets."""
from pathlib import Path
import csv
import itertools
import numpy as np
from mask import FIELDS

HERE=Path(__file__).resolve().parent
NAMES={"Hahn1":"copper","A":"mpg","B":"abalone"}
DEFAULT={f:options[0] for f,options in FIELDS.items()}
TOLERANCES=(0,.001,.01,.05)


def datasets():
    copper=np.loadtxt(HERE/"Hahn1.dat",skiprows=60)
    mpg=np.loadtxt(HERE/"auto-mpg.data",usecols=(2,0))
    abalone=np.loadtxt(HERE/"abalone.data",delimiter=",",usecols=(1,8))
    return {"Hahn1":(copper[:,1],copper[:,0]),"A":mpg.T,"B":abalone.T}


def fit(x,y,minimum,spec):
    keep=np.ones(len(y),dtype=bool) if spec["range"]=="all" else x>=minimum
    x,y=x[keep],y[keep]
    unique, rank=np.unique(x,return_inverse=True)
    n=len(unique)
    rule=spec["holdout"]
    if rule=="interleaved":
        test=rank%5==2
    elif rule=="middle":
        test=(rank>=int(.4*n)) & (rank<int(.6*n))
    else:
        test=rank>=int(.8*n)
    coord=x if spec["coordinate"]=="raw" else np.log(x)
    z=(coord-coord[~test].mean())/coord[~test].std()
    k1,k2=np.quantile(z[~test],[1/3,2/3])
    m1=np.c_[np.ones(len(z)),z,z*z,z**3]
    m2=np.c_[np.ones(len(z)),z,np.maximum(z-k1,0),np.maximum(z-k2,0)]
    bins=np.searchsorted(np.linspace(x[test].min(),x[test].max(),6)[1:-1],x[test],side="right")
    weights=np.ones(test.sum()) if spec["weights"]=="row" else 1/np.bincount(bins)[bins]
    scores=[]
    for design in (m1,m2):
        beta,_,rank,_=np.linalg.lstsq(design[~test],y[~test],rcond=None)
        assert rank==4
        scores.append(float(np.sqrt(np.average((design[test]@beta-y[test])**2,weights=weights))))
    return dict(**spec,cubic=scores[0],spline=scores[1],winner="cubic" if scores[0]<scores[1] else "spline",
                ntrain=int((~test).sum()),ntest=int(test.sum()))


def all_specs():
    return [dict(zip(FIELDS,vals)) for vals in itertools.product(*FIELDS.values())]


def matching(records,fields):
    return [r for r in records if all(r[k]==v for k,v in fields.items())]


def write(name,rows):
    with (HERE/name).open("w",newline="") as stream:
        out=csv.DictWriter(stream,fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def run():
    results=[]
    primary=[]
    for name,(x,y) in datasets().items():
        if not (np.isfinite(x).all() and np.isfinite(y).all() and (x>0).all()):
            raise ValueError("Invalid measured inputs for "+name)
        minimum=77 if name=="Hahn1" else float(np.median(x))
        scale=y.std()
        grid=[fit(x,y,minimum,spec) for spec in all_specs()]
        primary.extend(dict(dataset=NAMES[name],**r) for r in grid)
        for length in range(5):
            for retained in itertools.combinations(FIELDS,length):
                for tol in TOLERANCES:
                    ident=score_ident=guess=guess_scores=0
                    for r in grid:
                        partial={k:r[k] for k in retained}
                        group=matching(grid,partial)
                        point=matching(grid,DEFAULT|partial)[0]
                        s=np.array([[a["cubic"],a["spline"]] for a in group])
                        a=np.array([point["cubic"],point["spline"]])
                        b=np.array([r["cubic"],r["spline"]])
                        ident+=len({v["winner"] for v in group})==1
                        guess+=point["winner"]==r["winner"]
                        if tol:
                            score_ident+=np.ptp(s,axis=0).max()<=tol*scale
                            guess_scores+=abs(a-b).max()<=tol*scale
                        else:
                            score_ident+=np.ptp(np.round(s,8),axis=0).max()==0
                            guess_scores+=np.all(np.round(a,8)==np.round(b,8))
                    results.append(dict(dataset=NAMES[name],retained=",".join(retained) or "none",tol_sd=tol,
                                        winner_identified=ident,scores_identified=score_ident,
                                        default_winner_correct=guess,default_scores_correct=guess_scores,total=24))
    write("three_grids.csv",primary)
    write("recovery.csv",results)

if __name__=="__main__":
    run()
