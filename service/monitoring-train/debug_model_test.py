#!/usr/bin/env python3
"""
Fine-tuned 모델 테스트 디버깅 스크립트
결과 검증 및 문제점 파악
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

# 파일 경로 설정 (monitoring-train 서비스 내부)
REG_XLSX = Path("data/reg_test1.xlsx")
PAIR_CSV = Path("data/training_pairs_test1_noised_v1.csv")
MODEL_DIR = "../../llm_bge-m3"

def analyze_data_overlap():
    """데이터 중복 및 누출 확인"""
    print("🔍 데이터 중복 및 누출 확인...")
    
    # 데이터 로드
    reg = pd.read_excel(REG_XLSX).fillna("")
    reg.columns = [c.strip().lower() for c in reg.columns]
    reg = reg[["sid", "name"]].drop_duplicates()
    
    pair = pd.read_csv(PAIR_CSV).fillna("")
    pair.columns = [c.strip().lower() for c in pair.columns]
    pair = pair[["raw_name", "standard_substance_id"]].drop_duplicates()
    
    print(f"규정 데이터: {len(reg)}개")
    print(f"훈련 쌍 데이터: {len(pair)}개")
    
    # 중복 확인
    reg_names = set(reg["name"].str.lower().str.strip())
    pair_names = set(pair["raw_name"].str.lower().str.strip())
    
    overlap = reg_names.intersection(pair_names)
    print(f"이름 중복: {len(overlap)}개")
    print(f"중복 비율: {len(overlap)/len(pair_names)*100:.1f}%")
    
    if len(overlap) > 0:
        print("⚠️ 데이터 누출 가능성!")
        print("중복된 이름 예시:")
        for name in list(overlap)[:5]:
            print(f"  - {name}")
    
    return len(overlap) > 0

def test_with_different_data():
    """다른 데이터로 테스트"""
    print("\n🧪 다른 데이터로 테스트...")
    
    # 원본 데이터 로드
    reg = pd.read_excel(REG_XLSX).fillna("")
    reg.columns = [c.strip().lower() for c in reg.columns]
    reg = reg[["sid", "name"]].drop_duplicates()
    
    pair = pd.read_csv(PAIR_CSV).fillna("")
    pair.columns = [c.strip().lower() for c in pair.columns]
    pair = pair[["raw_name", "standard_substance_id"]].drop_duplicates()
    
    # 모델 로드
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_DIR, device=device)
    
    # 랜덤 샘플링으로 테스트
    test_size = min(100, len(pair))
    test_indices = np.random.choice(len(pair), test_size, replace=False)
    test_pair = pair.iloc[test_indices].copy()
    
    print(f"랜덤 테스트 샘플: {len(test_pair)}개")
    
    # 인코딩
    passage_embeddings = model.encode(
        [f"passage: {name}" for name in reg["name"].tolist()],
        normalize_embeddings=True,
        batch_size=256,
        show_progress_bar=False
    ).astype("float32")
    
    query_embeddings = model.encode(
        [f"query: {name}" for name in test_pair["raw_name"].tolist()],
        normalize_embeddings=True,
        batch_size=256,
        show_progress_bar=False
    ).astype("float32")
    
    # FAISS 인덱스
    index = faiss.IndexFlatIP(passage_embeddings.shape[1])
    index.add(passage_embeddings)
    
    # 검색
    scores, idxs = index.search(query_embeddings, 5)
    
    # 성능 계산
    hit1 = hit5 = 0
    for i, (sc, ix) in enumerate(zip(scores, idxs)):
        cands = [reg["sid"].iloc[j] for j in ix]
        gold = test_pair["standard_substance_id"].iloc[i]
        
        hit1 += int(cands[0] == gold)
        hit5 += int(gold in cands)
    
    recall1 = hit1 / len(test_pair)
    recall5 = hit5 / len(test_pair)
    
    print(f"랜덤 테스트 결과:")
    print(f"  Recall@1: {recall1:.3f} ({hit1}/{len(test_pair)})")
    print(f"  Recall@5: {recall5:.3f} ({hit5}/{len(test_pair)})")
    
    return recall1, recall5

def analyze_confidence_distribution():
    """신뢰도 분포 분석"""
    print("\n📊 신뢰도 분포 분석...")
    
    # 결과 파일 로드
    if os.path.exists("finetuned_retrieval_eval.csv"):
        results = pd.read_csv("finetuned_retrieval_eval.csv")
        
        print("신뢰도 통계:")
        print(f"  평균: {results['confidence'].mean():.3f}")
        print(f"  중앙값: {results['confidence'].median():.3f}")
        print(f"  최소값: {results['confidence'].min():.3f}")
        print(f"  최대값: {results['confidence'].max():.3f}")
        print(f"  표준편차: {results['confidence'].std():.3f}")
        
        # 히스토그램
        print("\n신뢰도 구간별 분포:")
        bins = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for i in range(len(bins)-1):
            count = len(results[(results['confidence'] >= bins[i]) & (results['confidence'] < bins[i+1])])
            percentage = count / len(results) * 100
            print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}: {count}개 ({percentage:.1f}%)")
    else:
        print("❌ 결과 파일이 없습니다.")

def test_confidence_formula():
    """신뢰도 공식 테스트"""
    print("\n🧮 신뢰도 공식 테스트...")
    
    if os.path.exists("finetuned_retrieval_eval.csv"):
        results = pd.read_csv("finetuned_retrieval_eval.csv")
        
        # 공식 재계산
        recalculated_conf = []
        for _, row in results.iterrows():
            top1 = row['score_top1']
            margin = row['margin']
            conf = 0.75 * top1 + 0.25 * margin
            recalculated_conf.append(conf)
        
        # 비교
        original_conf = results['confidence'].tolist()
        matches = sum(1 for a, b in zip(original_conf, recalculated_conf) if abs(a - b) < 1e-6)
        
        print(f"신뢰도 공식 일치: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)")
        
        if matches != len(results):
            print("⚠️ 신뢰도 공식에 문제가 있을 수 있습니다.")

def main():
    """메인 함수"""
    print("=" * 60)
    print("Fine-tuned 모델 테스트 디버깅")
    print("=" * 60)
    
    # 1. 데이터 중복 확인
    has_overlap = analyze_data_overlap()
    
    # 2. 다른 데이터로 테스트
    recall1, recall5 = test_with_different_data()
    
    # 3. 신뢰도 분포 분석
    analyze_confidence_distribution()
    
    # 4. 신뢰도 공식 테스트
    test_confidence_formula()
    
    # 5. 결과 요약
    print("\n" + "=" * 60)
    print("🔍 디버깅 결과 요약")
    print("=" * 60)
    
    if has_overlap:
        print("❌ 데이터 누출 의심: 훈련/테스트 데이터 중복")
    else:
        print("✅ 데이터 누출 없음")
    
    if recall1 > 0.95:
        print("⚠️ 랜덤 테스트에서도 높은 성능 - 모델이 과적합되었을 수 있음")
    else:
        print("✅ 랜덤 테스트 성능이 합리적")
    
    print(f"랜덤 테스트 Recall@1: {recall1:.3f}")
    print(f"랜덤 테스트 Recall@5: {recall5:.3f}")

if __name__ == "__main__":
    main()
