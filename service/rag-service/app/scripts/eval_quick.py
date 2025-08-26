# app/scripts/eval_quick.py
import re, json, pandas as pd
from app.query import QueryReq, query
from app.utils.progress import alive_range

CITE_RE=re.compile(r"\[[^\[\]\n]+?\]")
FALLBACK=re.compile(r"(제공된 자료 기준|확인되지 않습니다|정보가 없습니다|모릅니다)")

def eval_questions(csv_path, top_k=5, collections=None, max_n=100):
    if collections is None: collections=["sr_corpus","standards"]
    df=pd.read_csv(csv_path, encoding="utf-8")
    qs=df["question"].astype(str).tolist()[:max_n]
    n=len(qs); cite=fmt=fb=0
    for q in alive_range(qs, title="quick-eval"):
        res=query(QueryReq(question=q, top_k=top_k, collections=collections))
        a=res["answer"]
        if CITE_RE.search(a): cite+=1
        bullets=[ln for ln in a.splitlines() if ln.strip().startswith(("-", "•", "·"))]
        if 3<=len(bullets)<=6: fmt+=1
        if FALLBACK.search(a): fb+=1
    return {"n":n, "citation_rate":cite/n if n else 0, "format_score":fmt/n if n else 0, "fallback_rate":fb/n if n else 0}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--top_k", type=int, default=5)
    a=p.parse_args()
    print(json.dumps(eval_questions(a.csv, top_k=a.top_k), ensure_ascii=False, indent=2))
