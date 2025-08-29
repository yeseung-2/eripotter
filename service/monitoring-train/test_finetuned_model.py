#!/usr/bin/env python3
"""
Fine-tuned BGE-M3 모델 테스트 스크립트
GPU 최적화 및 성능 평가
"""

import pandas as pd
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from pathlib import Path
import time
import os
from typing import List, Dict, Tuple

# GPU 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 사용 디바이스: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

# 파일 경로 설정 (monitoring-train 서비스 내부)
REG_XLSX = Path("data/reg_test1.xlsx")
PAIR_CSV = Path("data/training_pairs_from_reg_hard5_typos3 (1).csv")
MODEL_DIR = "model/bomi-ai"  # BOMI AI 모델 경로

def check_files():
    """필요한 파일들이 존재하는지 확인"""
    print("🔍 파일 존재 여부 확인...")
    
    files_to_check = [
        ("규정 데이터 (Excel)", REG_XLSX),
        ("훈련 쌍 데이터 (CSV)", PAIR_CSV),
        ("Fine-tuned 모델", MODEL_DIR)
    ]
    
    all_exist = True
    for name, path in files_to_check:
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n⚠️ 일부 파일이 없습니다. 파일 경로를 확인해주세요.")
        return False
    
    print("✅ 모든 파일이 존재합니다.")
    return True

def load_data():
    """데이터 로드 및 전처리"""
    print("\n📊 데이터 로드 중...")
    
    # 규정 데이터 로드
    print("  규정 데이터 로드...")
    reg = pd.read_excel(REG_XLSX).fillna("")
    reg.columns = [c.strip().lower() for c in reg.columns]
    reg = reg[["sid", "name"]].drop_duplicates()
    print(f"    규정 데이터: {len(reg)}개 항목")
    
    # 훈련 쌍 데이터 로드
    print("  훈련 쌍 데이터 로드...")
    pair = pd.read_csv(PAIR_CSV).fillna("")
    pair.columns = [c.strip().lower() for c in pair.columns]
    pair = pair[["raw_name", "standard_substance_id"]].drop_duplicates()
    print(f"    훈련 쌍 데이터: {len(pair)}개 항목")
    
    return reg, pair

def load_model():
    """모델 로드"""
    print(f"\n🤖 모델 로드 중: {MODEL_DIR}")
    
    try:
        model = SentenceTransformer(MODEL_DIR, device=device)
        print(f"✅ 모델 로드 성공 (디바이스: {device})")
        return model
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None

def encode_texts(model, texts: List[str], prefix: str, batch_size: int = None):
    """텍스트 인코딩 (GPU 최적화)"""
    if batch_size is None:
        batch_size = 512 if torch.cuda.is_available() else 256
    
    print(f"  인코딩 중... (배치 크기: {batch_size})")
    start_time = time.time()
    
    encoded_texts = [f"{prefix}: {text}" for text in texts]
    embeddings = model.encode(
        encoded_texts, 
        normalize_embeddings=True, 
        batch_size=batch_size, 
        show_progress_bar=True,
        convert_to_numpy=True
    ).astype("float32")
    
    elapsed_time = time.time() - start_time
    print(f"  인코딩 완료: {len(texts)}개 텍스트, {elapsed_time:.2f}초")
    
    return embeddings

def build_index(passage_embeddings):
    """FAISS 인덱스 생성"""
    print("\n🔍 FAISS 인덱스 생성 중...")
    
    dimension = passage_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(passage_embeddings)
    
    print(f"✅ 인덱스 생성 완료 (차원: {dimension})")
    return index

def evaluate_model(index, query_embeddings, passage_sids: List[str], 
                  raw_names: List[str], gold_sids: List[str], top_k: int = 5):
    """모델 성능 평가"""
    print(f"\n📈 모델 성능 평가 중... (Top-{top_k})")
    
    start_time = time.time()
    scores, idxs = index.search(query_embeddings, top_k)
    elapsed_time = time.time() - start_time
    
    print(f"  검색 완료: {elapsed_time:.2f}초")
    
    # 성능 계산
    hit1 = hit5 = 0
    rows = []
    
    for i, (sc, ix) in enumerate(zip(scores, idxs)):
        cands = [passage_sids[j] for j in ix]
        top1, top2 = float(sc[0]), float(sc[1]) if len(sc) > 1 else 0.0
        margin = max(top1 - top2, 0.0)
        
        # 신뢰도 계산 방식 개선
        # top1 점수에 더 높은 가중치, margin에 낮은 가중치
        conf = 0.85 * top1 + 0.15 * margin
        
        # 신뢰도 밴드 결정 (원래 임계값 유지)
        if conf >= 0.70:
            band = "mapped"
        elif conf >= 0.40:
            band = "needs_review"
        else:
            band = "not_mapped"
        
        # 정확도 계산
        hit1 += int(cands[0] == gold_sids[i])
        hit5 += int(gold_sids[i] in cands)
        
        # 결과 저장
        rows.append({
            "raw_name": raw_names[i],
            "gold_sid": gold_sids[i],
            "pred_sid": cands[0],
            "score_top1": top1,
            "margin": margin,
            "confidence": conf,
            "band": band,
            "top5_sids": cands,
            "top5_scores": [float(s) for s in sc]
        })
    
    return hit1, hit5, len(gold_sids), rows

def save_results(results_df, hit1, hit5, total):
    """결과 저장"""
    print("\n💾 결과 저장 중...")
    
    # 성능 요약 출력
    recall1 = hit1 / total
    recall5 = hit5 / total
    
    print(f"📊 성능 결과:")
    print(f"  Recall@1: {recall1:.3f} ({hit1}/{total})")
    print(f"  Recall@5: {recall5:.3f} ({hit5}/{total})")
    
    # 신뢰도 밴드별 분포 및 정확도
    band_counts = results_df['band'].value_counts()
    print(f"\n🎯 신뢰도 밴드별 분포:")
    for band, count in band_counts.items():
        percentage = count / len(results_df) * 100
        print(f"  {band}: {count}개 ({percentage:.1f}%)")
    
    # Mapped 케이스의 Precision 계산
    mapped_df = results_df[results_df['band'] == 'mapped']
    if len(mapped_df) > 0:
        mapped_correct = (mapped_df['gold_sid'] == mapped_df['pred_sid']).sum()
        mapped_precision = mapped_correct / len(mapped_df)
        print(f"\n🎯 Mapped 케이스 정확도 (Precision):")
        print(f"  Precision: {mapped_precision:.3f} ({mapped_correct}/{len(mapped_df)})")
        
        # Needs_review 케이스의 정확도도 계산
        review_df = results_df[results_df['band'] == 'needs_review']
        if len(review_df) > 0:
            review_correct = (review_df['gold_sid'] == review_df['pred_sid']).sum()
            review_precision = review_correct / len(review_df)
            print(f"  Needs_review 정확도: {review_precision:.3f} ({review_correct}/{len(review_df)})")
    
    # 결과 저장
    output_file = "finetuned_retrieval_eval.csv"
    results_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"✅ 결과 저장 완료: {output_file}")
    
    return recall1, recall5

def main():
    """메인 함수"""
    print("=" * 60)
    print("Fine-tuned BGE-M3 모델 테스트")
    print("=" * 60)
    
    # 1. 파일 확인
    if not check_files():
        return
    
    # 2. 데이터 로드
    reg, pair = load_data()
    
    # 3. 모델 로드
    model = load_model()
    if model is None:
        return
    
    # 4. 텍스트 인코딩
    print("\n🔄 텍스트 인코딩 중...")
    
    # Passage 인코딩
    passage_embeddings = encode_texts(model, reg["name"].tolist(), "passage")
    
    # Query 인코딩
    query_embeddings = encode_texts(model, pair["raw_name"].tolist(), "query")
    
    # 5. FAISS 인덱스 생성
    index = build_index(passage_embeddings)
    
    # 6. 모델 평가
    hit1, hit5, total, rows = evaluate_model(
        index, 
        query_embeddings, 
        reg["sid"].tolist(),
        pair["raw_name"].tolist(),
        pair["standard_substance_id"].tolist()
    )
    
    # 7. 결과 저장
    results_df = pd.DataFrame(rows)
    recall1, recall5 = save_results(results_df, hit1, hit5, total)
    
    # 8. 최종 요약
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("=" * 60)
    print(f"📊 최종 성능:")
    print(f"  Recall@1: {recall1:.3f}")
    print(f"  Recall@5: {recall5:.3f}")
    print(f"  총 테스트 샘플: {total}개")
    
    if torch.cuda.is_available():
        print(f"\n🚀 GPU 메모리 사용량:")
        print(f"  할당됨: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
        print(f"  캐시됨: {torch.cuda.memory_reserved() / 1024**3:.2f}GB")

if __name__ == "__main__":
    main()
