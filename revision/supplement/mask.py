"""Generate masked assignments and the separate scoring key from the fixed analysis plan."""
import itertools
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
FIELDS = {
    "range": ["all","upper"],
    "holdout":["interleaved","middle","hot"],
    "coordinate":["raw","log"],
    "weights":["row","bins"],
}

def assignments():
    rng=np.random.default_rng(79139512)
    specs=[dict(zip(FIELDS,values)) for values in itertools.product(*FIELDS.values())]
    public, keys = [], []
    for dataset in ("A","B"):
        indices=rng.choice(len(specs),6,replace=False)
        for index,(selected,nfields) in enumerate(zip(indices,(2,2,3,3,4,4))):
            spec=specs[int(selected)]
            fields=set(rng.choice(list(FIELDS),nfields,replace=False))
            label=dataset+str(1+index)
            public.append(dict(id=label,fields={f:spec[f] for f in FIELDS if f in fields}))
            keys.append(dict(id=label,spec=spec))
    return public, keys

if __name__=="__main__":
    public, keys=assignments()
    private=Path(sys.argv[1])
    private.mkdir(parents=True,exist_ok=True)
    (private/"key.json").write_text(json.dumps(keys,indent=2))
    (HERE/"masked_cases.json").write_text(json.dumps(public,indent=2))
