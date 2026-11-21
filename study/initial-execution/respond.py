"""Two-choice inference. This program reads prompts and public weights only."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from llama_cpp import Llama, __version__

MODELS={
 'Qwen2.5-0.5B-Instruct':('Qwen/Qwen2.5-0.5B-Instruct-GGUF','9217f5db79a29953eb74d5343926648285ec7e67','qwen2.5-0.5b-instruct-q4_k_m.gguf','74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db'),
 'SmolLM2-135M-Instruct':('bartowski/SmolLM2-135M-Instruct-GGUF','09816acd5d99df7be770d85ea30822623dab342c','SmolLM2-135M-Instruct-Q4_K_M.gguf','2e8040ceae7815abe0dcb3540b9995eaa1fa0d2ca9e797d0a635ae4433c68c2d'),
}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--prompts',type=Path,required=True);ap.add_argument('--weights',type=Path,required=True)
    ap.add_argument('--model',choices=MODELS,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--threads',type=int,default=2)
    args=ap.parse_args(); spec=MODELS[args.model];start=datetime.now(timezone.utc).isoformat()
    assert hashlib.file_digest(args.weights.open('rb'),'sha256').hexdigest()==spec[-1]
    source=json.loads(args.prompts.read_text())
    bot=Llama(model_path=str(args.weights),n_threads=args.threads,n_threads_batch=args.threads,
              n_ctx=256,n_batch=256,n_gpu_layers=0,verbose=False)
    template=bot.metadata['tokenizer.chat_template']
    assert '<|im_start|>' in template and '<|im_end|>' in template
    a,b=(bot.tokenize(x,add_bos=False) for x in (b'A',b'B'))
    assert len(a)==len(b)==1
    prior=[]; entries=[]
    for case in source['cases']:
        text=('<|im_start|>system\n'+source['system']+'<|im_end|>\n<|im_start|>user\n'+case['user']+
              '<|im_end|>\n<|im_start|>assistant\n')
        tok=bot.tokenize(text.encode(),add_bos=False,special=True)
        prefix=0
        for x,y in zip(prior[:-1],tok[:-1]):
            if x!=y:break
            prefix+=1
        bot.n_tokens=prefix
        bot.eval(tok[prefix:])
        logits=bot._ctx.get_logits()
        la,lb=float(logits[a[0]]),float(logits[b[0]])
        assert np.isfinite([la,lb]).all()
        entries.append(dict(pair=case['pair'],condition=case['condition'],selection='A' if la>=lb else 'B',logit_A=la,logit_B=lb,prompt_sha256=hashlib.sha256(text.encode()).hexdigest()))
        prior=tok
    with args.out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(entries[0]));w.writeheader();w.writerows(entries)
    details=dict(model=args.model,repository=spec[0],revision=spec[1],filename=spec[2],sha256=spec[-1],engine='llama-cpp-python',version=__version__,threads=args.threads,started_utc=start,ended_utc=datetime.now(timezone.utc).isoformat(),token_A=a,token_B=b,number_of_responses=len(entries),chat_template=template,architecture=bot.metadata.get('general.architecture'))
    args.out.with_suffix('.json').write_text(json.dumps(details,indent=2)+'\n')
    print(args.out, len(entries),flush=True)
if __name__=='__main__':main()
