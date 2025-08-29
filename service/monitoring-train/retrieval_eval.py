# pip install sentence-transformers faiss-cpu pandas openpyxl
import pandas as pd, numpy as np, faiss, os
from sentence_transformers import SentenceTransformer

REG_XLSX = "./data/reg_test1.xlsx"          # sid,name
PAIR_CSV = "./data/training_pairs_from_reg_hard5_typos3 (1).csv" # raw_name,standard_substance_id (노이즈 데이터)
MODEL_DIR = "../../llm_bge-m3"              # 로컬 베이스 모델 (파인튜닝 전)

reg = pd.read_excel(REG_XLSX).fillna("")
reg = reg.rename(columns=lambda c: str(c).strip().lower())
reg = reg[["sid","name"]].dropna().drop_duplicates()

pair = pd.read_csv(PAIR_CSV).fillna("")
pair = pair.rename(columns=lambda c: str(c).strip().lower())

# NaN 값 제거 - 실제 매핑 가능한 데이터만 사용
pair = pair[["raw_name","standard_substance_id"]].dropna()
print(f"📊 원본 데이터: {len(pair)}개")
print(f"📊 NaN 제거 후: {len(pair)}개")

# 추가 필터링: 빈 문자열이나 의미없는 값 제거
pair = pair[pair["raw_name"].str.strip() != ""]
pair = pair[pair["standard_substance_id"].str.strip() != ""]
print(f"📊 최종 평가 데이터: {len(pair)}개")

model = SentenceTransformer(MODEL_DIR)

def enc_passage(texts):  # passage prefix 권장
    return model.encode([f"passage: {t}" for t in texts], normalize_embeddings=True,
                        batch_size=32, show_progress_bar=True).astype("float32")
def enc_query(texts):
    return model.encode([f"query: {t}" for t in texts], normalize_embeddings=True,
                        batch_size=32, show_progress_bar=True).astype("float32")

# 1) 인덱스 구축
print(f"🔄 표준 필드 임베딩 생성 중... ({len(reg)}개)")
p_texts = reg["name"].astype(str).tolist()
p_vecs = enc_passage(p_texts)
print(f"✅ 표준 필드 임베딩 완료: {p_vecs.shape}")

print("🔄 FAISS 인덱스 구축 중...")
index = faiss.IndexFlatIP(p_vecs.shape[1])
index.add(p_vecs)
p_sids = reg["sid"].tolist()
print("✅ FAISS 인덱스 구축 완료")

# 2) 평가 (Recall@1/5, 점수/마진 → 신뢰도)
print(f"🔄 쿼리 임베딩 생성 중... ({len(pair)}개)")
q_texts = pair["raw_name"].astype(str).tolist()
q_vecs = enc_query(q_texts)
print(f"✅ 쿼리 임베딩 완료: {q_vecs.shape}")

print("🔄 FAISS 검색 및 평가 중...")
scores, idxs = index.search(q_vecs, 5)
print("✅ FAISS 검색 완료")

gold = pair["standard_substance_id"].tolist()
hit1 = hit5 = 0
rows = []
for i, (sc, ix) in enumerate(zip(scores, idxs)):
    cands = [p_sids[j] for j in ix]
    top1_sid, top1 = cands[0], float(sc[0])
    top2 = float(sc[1]) if len(sc) > 1 else 0.0
    margin = max(top1 - top2, 0.0)
    # 간단 신뢰도(캘리브레이션 전): 가중합
    conf = 0.75 * top1 + 0.25 * margin
    band = "mapped" if conf >= 0.80 else ("needs_review" if conf >= 0.50 else "not_mapped")
    is1 = (top1_sid == gold[i]); hit1 += int(is1)
    is5 = int(gold[i] in cands); hit5 += is5
    rows.append({
        "raw_name": q_texts[i],
        "gold_sid": gold[i],
        "pred_sid": top1_sid,
        "score_top1": top1,
        "margin": margin,
        "confidence": conf,
        "band": band,
        "top5_sids": cands,
        "top5_scores": [float(s) for s in sc]
    })

print(f"Recall@1 = {hit1/len(gold):.3f} | Recall@5 = {hit5/len(gold):.3f}")

# 3) 결과 저장
out = pd.DataFrame(rows)
out.to_csv("./data/retrieval_eval_results.csv", index=False, encoding="utf-8-sig")
print("saved: ./data/retrieval_eval_results.csv")
