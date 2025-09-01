#!/usr/bin/env python3
"""
운영 지표 중심 평가 스크립트
Precision(mapped) ≥ 0.97 조건에서 Coverage 최대화
"""

import pandas as pd
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from pathlib import Path
import time
from typing import List, Dict, Tuple

# GPU 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 사용 디바이스: {device}")

# 파일 경로 설정
REG_XLSX = Path("data/reg_test1.xlsx")
PAIR_CSV = Path("data/training_pairs_from_reg_hard5_typos3 (1).csv")
MODEL_DIR = "model/bomi-ai"  # BOMI AI 모델 경로

def load_data():
    """데이터 로드"""
    print("📊 데이터 로드 중...")
    
    # 규정 데이터
    reg = pd.read_excel(REG_XLSX).fillna("")
    reg.columns = [c.strip().lower() for c in reg.columns]
    reg = reg[["sid", "name"]].drop_duplicates()
    
    # 훈련 쌍 데이터
    pair = pd.read_csv(PAIR_CSV).fillna("")
    pair.columns = [c.strip().lower() for c in pair.columns]
    pair = pair[["raw_name", "standard_substance_id"]].drop_duplicates()
    
    return reg, pair

def load_model():
    """모델 로드"""
    print(f"🤖 모델 로드 중: {MODEL_DIR}")
    model = SentenceTransformer(MODEL_DIR, device=device)
    return model

def encode_texts(model, texts: List[str], prefix: str, batch_size: int = 512):
    """텍스트 인코딩"""
    encoded_texts = [f"{prefix}: {text}" for text in texts]
    embeddings = model.encode(
        encoded_texts, 
        normalize_embeddings=True, 
        batch_size=batch_size, 
        show_progress_bar=True
    ).astype("float32")
    return embeddings

def calculate_confidence(top1_score: float, margin: float) -> float:
    """신뢰도 계산: 0.75*top1 + 0.25*margin"""
    return 0.75 * top1_score + 0.25 * max(margin, 0.0)

def evaluate_with_threshold(results_df: pd.DataFrame, confidence_threshold: float) -> Dict:
    """특정 신뢰도 임계값에서 성능 평가"""
    # 신뢰도 밴드 결정
    mapped_mask = results_df['confidence'] >= confidence_threshold
    mapped_df = results_df[mapped_mask]
    
    if len(mapped_df) == 0:
        return {
            'threshold': confidence_threshold,
            'precision': 0.0,
            'coverage': 0.0,
            'mapped_count': 0,
            'total_count': len(results_df)
        }
    
    # Precision 계산
    correct_mapped = (mapped_df['gold_sid'] == mapped_df['pred_sid']).sum()
    precision = correct_mapped / len(mapped_df)
    
    # Coverage 계산
    coverage = len(mapped_df) / len(results_df)
    
    return {
        'threshold': confidence_threshold,
        'precision': precision,
        'coverage': coverage,
        'mapped_count': len(mapped_df),
        'total_count': len(results_df),
        'correct_mapped': correct_mapped
    }

def find_optimal_threshold(results_df: pd.DataFrame, min_precision: float = 0.97) -> Dict:
    """Precision ≥ 0.97 조건에서 Coverage 최대화하는 임계값 찾기"""
    print(f"🔍 최적 임계값 탐색 중 (최소 Precision: {min_precision})...")
    
    # 신뢰도 범위에서 그리드 스윕
    thresholds = np.arange(0.3, 0.95, 0.01)
    results = []
    
    for threshold in thresholds:
        result = evaluate_with_threshold(results_df, threshold)
        results.append(result)
    
    results_df = pd.DataFrame(results)
    
    # Precision ≥ 0.97 조건 만족하는 것들 중 Coverage 최대
    valid_results = results_df[results_df['precision'] >= min_precision]
    
    if len(valid_results) == 0:
        print(f"⚠️ Precision {min_precision} 이상인 임계값이 없습니다.")
        # 가장 높은 Precision 찾기
        best_idx = results_df['precision'].idxmax()
        best_result = results_df.loc[best_idx]
        print(f"최고 Precision: {best_result['precision']:.3f} (임계값: {best_result['threshold']:.2f})")
        return best_result.to_dict()
    
    # Coverage 최대화
    best_idx = valid_results['coverage'].idxmax()
    best_result = valid_results.loc[best_idx]
    
    print(f"✅ 최적 임계값: {best_result['threshold']:.2f}")
    print(f"  Precision: {best_result['precision']:.3f}")
    print(f"  Coverage: {best_result['coverage']:.3f}")
    
    return best_result.to_dict()

def main():
    """메인 함수"""
    print("=" * 60)
    print("운영 지표 중심 평가")
    print("=" * 60)
    
    # 1. 데이터 로드
    reg, pair = load_data()
    print(f"✅ 규정 데이터: {len(reg)}개")
    print(f"✅ 훈련 쌍 데이터: {len(pair)}개")
    
    # 2. 모델 로드
    model = load_model()
    
    # 3. 텍스트 인코딩
    print("\n🔄 텍스트 인코딩 중...")
    passage_embeddings = encode_texts(model, reg["name"].tolist(), "passage")
    query_embeddings = encode_texts(model, pair["raw_name"].tolist(), "query")
    
    # 4. FAISS 인덱스 생성
    print("\n🔍 FAISS 인덱스 생성 중...")
    index = faiss.IndexFlatIP(passage_embeddings.shape[1])
    index.add(passage_embeddings)
    
    # 5. 검색 및 평가
    print("\n📈 검색 및 평가 중...")
    scores, idxs = index.search(query_embeddings, 5)
    
    # 6. 결과 분석
    rows = []
    for i, (sc, ix) in enumerate(zip(scores, idxs)):
        cands = [reg["sid"].iloc[j] for j in ix]
        top1_score = float(sc[0])
        top2_score = float(sc[1]) if len(sc) > 1 else 0.0
        margin = max(top1_score - top2_score, 0.0)
        
        # 신뢰도 계산
        confidence = calculate_confidence(top1_score, margin)
        
        rows.append({
            "raw_name": pair["raw_name"].iloc[i],
            "gold_sid": pair["standard_substance_id"].iloc[i],
            "pred_sid": cands[0],
            "score_top1": top1_score,
            "margin": margin,
            "confidence": confidence,
            "top5_sids": cands,
            "top5_scores": [float(s) for s in sc]
        })
    
    results_df = pd.DataFrame(rows)
    
    # 7. 최적 임계값 찾기
    optimal_result = find_optimal_threshold(results_df, min_precision=0.97)
    
    # 8. 상세 분석
    print("\n📊 상세 분석 결과:")
    print(f"  최적 신뢰도 임계값: {optimal_result['threshold']:.2f}")
    print(f"  Precision: {optimal_result['precision']:.3f}")
    print(f"  Coverage: {optimal_result['coverage']:.3f}")
    print(f"  자동 매핑 개수: {optimal_result['mapped_count']}/{optimal_result['total_count']}")
    
    # 9. 신뢰도 분포
    print("\n🎯 신뢰도 분포:")
    confidence_ranges = [
        (0.0, 0.5, "낮음"),
        (0.5, 0.7, "보통"),
        (0.7, 0.9, "높음"),
        (0.9, 1.0, "매우 높음")
    ]
    
    for low, high, label in confidence_ranges:
        count = len(results_df[(results_df['confidence'] >= low) & (results_df['confidence'] < high)])
        percentage = count / len(results_df) * 100
        print(f"  {label} ({low:.1f}-{high:.1f}): {count}개 ({percentage:.1f}%)")
    
    # 10. 결과 저장
    output_file = "operational_evaluation_results.csv"
    results_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\n💾 결과 저장 완료: {output_file}")
    
    # 11. 최종 요약
    print("\n" + "=" * 60)
    print("🎉 운영 지표 평가 완료!")
    print("=" * 60)
    print(f"📈 최적 운영 설정:")
    print(f"  신뢰도 임계값: {optimal_result['threshold']:.2f}")
    print(f"  예상 Precision: {optimal_result['precision']:.3f}")
    print(f"  예상 Coverage: {optimal_result['coverage']:.3f}")
    print(f"  자동 매핑 비율: {optimal_result['coverage']*100:.1f}%")

if __name__ == "__main__":
    main()
