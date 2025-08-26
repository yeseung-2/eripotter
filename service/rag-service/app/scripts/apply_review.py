# app/scripts/apply_review.py
from __future__ import annotations
import json, csv
from pathlib import Path
from app.utils.progress import alive_range

SYS = "너는 ESG/TCFD 보고서 초안 보조자다. 한국어로 간결히 작성하고, 일관된 인용/형식을 유지한다."

def load_jsonl(p:Path):
    items=[]
    with p.open(encoding="utf-8") as f:
        for ln in f:
            ln=ln.strip()
            if ln: items.append(json.loads(ln))
    return items

def dump_jsonl(items, p:Path):
    with p.open("w", encoding="utf-8") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False)+"\n")

def to_msg(q,a):
    return {"messages":[
        {"role":"system","content":SYS},
        {"role":"user","content":q},
        {"role":"assistant","content":a},
    ]}

def main(review_csv, base_train, base_val, out_train_sft, out_val_sft, out_dpo):
    edits={}
    with Path(review_csv).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        for row in alive_range(rows, title="apply-review"):
            if row.get("keep_YN","").strip().upper()=="Y" and row.get("edited_answer","").strip():
                edits[row["question"].strip()]=row["edited_answer"].strip()

    train=load_jsonl(Path(base_train)); val=load_jsonl(Path(base_val))

    def apply(ds):
        out=[]
        for it in ds:
            q=it["messages"][1]["content"]; a=it["messages"][2]["content"]
            if q in edits: a=edits[q]
            out.append(to_msg(q,a))
        return out

    train2=apply(train); val2=apply(val)
    dump_jsonl(train2, Path(out_train_sft)); dump_jsonl(val2, Path(out_val_sft))

    # DPO (리뷰 있는 항목만)
    dpo=[]
    for it in train:
        q=it["messages"][1]["content"]; a=it["messages"][2]["content"]
        if q in edits:
            dpo.append({"prompt":f"<QUESTION>\n{q}", "chosen":edits[q], "rejected":a})
    if dpo:
        dump_jsonl(dpo, Path(out_dpo))
        print(f"[apply_review] DPO samples: {len(dpo)}")

    print(f"[apply_review] edits={len(edits)} -> SFT:{out_train_sft}/{out_val_sft} DPO:{out_dpo if dpo else 'none'}")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--review_csv", default="./data/datasets/review_queue.csv")
    p.add_argument("--train_in", default="./data/datasets/train_sft.jsonl")
    p.add_argument("--val_in", default="./data/datasets/val_sft.jsonl")
    p.add_argument("--train_out", default="./data/datasets/train_sft_reviewed.jsonl")
    p.add_argument("--val_out", default="./data/datasets/val_sft_reviewed.jsonl")
    p.add_argument("--dpo_out", default="./data/datasets/train_dpo.jsonl")
    a=p.parse_args()
    main(a.review_csv, a.train_in, a.val_in, a.train_out, a.val_out, a.dpo_out)
