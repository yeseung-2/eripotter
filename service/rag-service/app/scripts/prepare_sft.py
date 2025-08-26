# app/scripts/prepare_sft.py
from __future__ import annotations
import json, re, hashlib, random, csv
from pathlib import Path
from typing import List, Dict
from app.utils.progress import alive_range

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
            if not ln: continue
            try: out.append(json.loads(ln))
            except: pass
    return out

def tokenize(s:str)->List[str]:
    import re
    return re.findall(r"[가-힣A-Za-z0-9]+", s or "")

def ko_ratio(s:str)->float:
    import re
    return (len(re.findall(r"[가-힣]", s)) / max(1,len(s)))

def ngrams(toks:List[str], n:int=3):
    return list(zip(*[toks[i:] for i in range(n)])) if len(toks)>=n else []

def grounding_score(a:str, chunks:List[Dict], n:int=3)->float:
    at=set(ngrams(tokenize(a), n))
    if not at: return 0.0
    ctx=" ".join((c.get("text") or "") for c in (chunks or []))
    ct=set(ngrams(tokenize(ctx), n))
    return len(at & ct)/max(1,len(at))

def messages_record(q: str, a: str) -> dict:
    return {
        "messages": [
            {   "role": "system",
                "content": (
                    "역할: 지속가능경영보고서 기반 RAG 답변을 기반으로 솔루션을 제시하는 컨설턴트다다. "
                    "항상 한국어로 간결하고 전문적으로 작성한다. "
                    "출력은 정확히 3개의 HTML 문단으로만 구성한다: <p>활동:…</p><p>방법:…</p><p>목표:…</p>. "
                    "예: <p>활동: 산업안전보건위원회 정기 운영</p><p>방법: 분기별 회의 및 자율점검 체계 구축</p><p>목표: 산업재해 예방을 위한 현장 안전관리 강화</p>"
                    "SOURCES 밖 내용 추가·가정 금지, URL/파일명 등 메타데이터 본문 노출 금지. "),
            },
            {"role": "user", "content": q},
            {"role": "assistant", "content": a},
        ]
    }


def main(src_path:str, out_dir:str, val_ratio:float):
    src=Path(src_path); outd=Path(out_dir); outd.mkdir(parents=True, exist_ok=True)
    train_out=outd/"train_sft.jsonl"; val_out=outd/"val_sft.jsonl"; review_csv=outd/"review_queue.csv"

    logs=read_jsonl(src)
    kept=[]; rejected=[]; seen=set()

    for lg in alive_range(logs, title="cleaning"):
        q=(lg.get("input") or lg.get("question") or "").strip()
        a=(lg.get("output") or lg.get("answer") or "").strip()
        if not q or not a: rejected.append("missing_q_or_a"); continue
        if not (MIN_Q_TOK<=len(tokenize(q))<=MAX_Q_TOK): rejected.append("q_len"); continue
        if not (MIN_A_TOK<=len(tokenize(a))<=MAX_A_TOK): rejected.append("a_len"); continue
        if ko_ratio(q+" "+a) < LANG_KO_RATIO_THR: rejected.append("low_ko_ratio"); continue
        import re as _re
        if any(_re.search(p,a) for p in INVALID_ANS_PATTERNS): rejected.append("invalid_answer"); continue
        chunks=lg.get("retrieved_chunks") or []
        if chunks:
            gs=grounding_score(a, chunks, 3)
            if gs<GROUNDING_THR: rejected.append(f"low_grounding:{gs:.3f}"); continue
        else:
            gs=0.0
        h=hashlib.sha1((q+"\n"+a).encode("utf-8")).hexdigest()
        if h in seen: rejected.append("duplicate"); continue
        seen.add(h)
        kept.append({"qid":lg.get("qid"),"question":q,"answer":a,"grounding":gs})

    # 리뷰 후보 (grounding 낮은 순 상위 500)
    import csv as _csv
    cand=sorted(kept, key=lambda x: (x["grounding"] if x["grounding"]>0 else 1.0))[:500]
    if cand:
        with review_csv.open("w", newline="", encoding="utf-8") as f:
            w=_csv.DictWriter(f, fieldnames=["qid","question","answer","grounding","keep_YN","edited_answer","notes"])
            w.writeheader()
            for c in cand:
                w.writerow({"qid":c.get("qid") or "","question":c["question"],"answer":c["answer"],
                            "grounding":f"{c['grounding']:.3f}","keep_YN":"","edited_answer":"","notes":""})

    # messages 변환 + train/val 분할
    samples=[messages_record(x["question"],x["answer"]) for x in kept]
    random.seed(42); random.shuffle(samples)
    n=len(samples); cut=max(1,int(n*val_ratio)) if n>1 else n
    val=samples[:cut]; train=samples[cut:]

    with train_out.open("w",encoding="utf-8") as f:
        for s in train: f.write(json.dumps(s, ensure_ascii=False)+"\n")
    with val_out.open("w",encoding="utf-8") as f:
        for s in val: f.write(json.dumps(s, ensure_ascii=False)+"\n")

    print(f"[prepare_sft] kept={len(kept)} rejected={len(rejected)} total={len(logs)}")
    print(f"  train={len(train)} val={len(val)} out_dir={out_dir}")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--src", default="./data/logs/qa_runs.jsonl")
    p.add_argument("--out_dir", default="./data/datasets")
    p.add_argument("--val_ratio", type=float, default=0.1)
    a=p.parse_args()
    main(a.src, a.out_dir, a.val_ratio)
