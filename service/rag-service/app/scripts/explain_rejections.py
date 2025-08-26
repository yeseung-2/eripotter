from __future__ import annotations
import json, re, hashlib, csv
from pathlib import Path
from typing import List, Dict
from collections import Counter

# === prepare_sft.py와 동일 기준 ===
MIN_Q_TOK=3; MAX_Q_TOK=128
MIN_A_TOK=10; MAX_A_TOK=900
GROUNDING_THR=0.18
LANG_KO_RATIO_THR=0.35
INVALID_ANS_PATTERNS=[r"제공된 자료 기준", r"확인되지 않습니다", r"정보가 없습니다", r"모릅니다"]

def read_jsonl(p:Path)->List[dict]:
    out=[]
    with p.open(encoding="utf-8") as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                try: out.append(json.loads(ln))
                except: pass
    return out

def tokenize(s:str)->List[str]:
    return re.findall(r"[가-힣A-Za-z0-9]+", s or "")

def ko_ratio(s:str)->float:
    return (len(re.findall(r"[가-힣]", s)) / max(1,len(s)))

def ngrams(toks:List[str], n:int=3):
    return list(zip(*[toks[i:] for i in range(n)])) if len(toks)>=n else []

def grounding_score(a:str, chunks:List[Dict], n:int=3)->float:
    at=set(ngrams(tokenize(a), n))
    if not at: return 0.0
    ctx=" ".join((c.get("text") or "") for c in (chunks or []))
    ct=set(ngrams(tokenize(ctx), n))
    return len(at & ct)/max(1,len(at))

def main(src_path:str, out_csv:str|None=None, sample_n:int=200):
    logs=read_jsonl(Path(src_path))
    reasons=Counter()
    samples=[]

    seen=set()
    for lg in logs:
        q=(lg.get("input") or lg.get("question") or "").strip()
        a=(lg.get("output") or lg.get("answer") or "").strip()
        if not q or not a:
            reasons["missing_q_or_a"]+=1
            if len(samples)<sample_n: samples.append(("missing_q_or_a", q, a)); continue

        if not (MIN_Q_TOK<=len(tokenize(q))<=MAX_Q_TOK):
            reasons["q_len"]+=1
            if len(samples)<sample_n: samples.append(("q_len", q, a)); continue

        if not (MIN_A_TOK<=len(tokenize(a))<=MAX_A_TOK):
            reasons["a_len"]+=1
            if len(samples)<sample_n: samples.append(("a_len", q, a)); continue

        if ko_ratio(q+" "+a) < LANG_KO_RATIO_THR:
            reasons["low_ko_ratio"]+=1
            if len(samples)<sample_n: samples.append(("low_ko_ratio", q, a)); continue

        if any(re.search(p,a) for p in INVALID_ANS_PATTERNS):
            reasons["invalid_answer"]+=1
            if len(samples)<sample_n: samples.append(("invalid_answer", q, a)); continue

        chunks=lg.get("retrieved_chunks") or []
        if chunks:
            gs=grounding_score(a, chunks, 3)
            if gs<GROUNDING_THR:
                reasons[f"low_grounding"]+=1
                if len(samples)<sample_n: samples.append((f"low_grounding:{gs:.3f}", q, a)); continue
        else:
            # prepare_sft는 chunks 없으면 사실상 0으로 간주하고 버려짐
            reasons["no_chunks/low_grounding"]+=1
            if len(samples)<sample_n: samples.append(("no_chunks/low_grounding", q, a)); continue

        h=hashlib.sha1((q+"\n"+a).encode("utf-8")).hexdigest()
        if h in seen:
            reasons["duplicate"]+=1
            if len(samples)<sample_n: samples.append(("duplicate", q, a)); continue
        seen.add(h)

    # 결과 출력
    total=len(logs); rejected=sum(reasons.values())
    print(f"total={total} rejected={rejected} kept={total-rejected}")
    for k,v in reasons.most_common():
        print(f"{k}: {v}")

    if out_csv:
        outp=Path(out_csv); outp.parent.mkdir(parents=True, exist_ok=True)
        with outp.open("w", newline="", encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["reason","question","answer"])
            for r,q,a in samples:
                w.writerow([r,q,a])
        print(f"sampled rejects -> {out_csv}")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--src", default="./data/logs/qa_runs.jsonl")
    p.add_argument("--out_csv", default="./data/datasets/reject_samples.csv")
    p.add_argument("--sample_n", type=int, default=200)
    a=p.parse_args()
    main(a.src, a.out_csv, a.sample_n)
