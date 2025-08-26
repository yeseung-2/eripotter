import os, time, pandas as pd
from app.query import QueryReq, query  # /rag/query와 동일 로직 + JSONL 로깅 수행
from app.utils.progress import alive_range

def main(csv_path: str, top_k: int = 8, collections=None, out_log_path: str | None = None, sleep_sec: float = 0.0):
    # 기본 컬렉션: 환경변수 우선 → 없으면 통일된 기본값
    if collections is None or len(collections) == 0:
        collections = [
            os.getenv("SR_COLLECTION", "sr_corpus"),
            os.getenv("STD_COLLECTION", "standards"),
        ]

    # 배치 결과를 별도 파일로 기록하려면 out_log_path 지정
    if out_log_path:
        os.makedirs(os.path.dirname(out_log_path), exist_ok=True)
        os.environ["QA_JSONL_PATH"] = out_log_path

    df = pd.read_csv(csv_path, encoding="utf-8")
    if "question" not in df.columns:
        raise ValueError("CSV에 'question' 컬럼이 필요합니다.")

    total = ok = 0
    iterable = df["question"].astype(str).fillna("").map(str.strip)
    for q in alive_range(iterable, title="batch-rag"):
        total += 1
        if not q:
            continue
        try:
            req = QueryReq(question=q, top_k=top_k, collections=collections)
            _ = query(req)  # 내부 호출 → jsonl 자동 로깅(근거 없으면 내부에서 스킵)
            ok += 1
        except Exception as e:
            print(f"[WARN] 실패: {q[:60]}... -> {e}")
        if sleep_sec > 0:
            time.sleep(sleep_sec)
    print(f"[DONE] total={total}, success={ok}, log={os.getenv('QA_JSONL_PATH')}")
    

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--top_k", type=int, default=8)
    p.add_argument("--collections", nargs="*", default=[])
    p.add_argument("--out_log", default="")
    p.add_argument("--sleep", type=float, default=0.0)
    a = p.parse_args()
    main(a.csv, a.top_k, a.collections or None, a.out_log or None, a.sleep)
