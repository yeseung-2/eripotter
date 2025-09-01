#!/usr/bin/env python3
"""
평가용 데이터 정리 스크립트
NaN 값을 제거하고 실제 매핑 가능한 데이터만 추출
"""

import pandas as pd
from pathlib import Path

# 파일 경로
INPUT_CSV = Path("data/training_pairs_from_reg_hard5_typos3 (1).csv")
OUTPUT_CSV = Path("data/evaluation_pairs_clean.csv")

def clean_evaluation_data():
    """평가용 데이터 정리"""
    print("🧹 평가용 데이터 정리 중...")
    
    # 원본 데이터 로드
    df = pd.read_csv(INPUT_CSV).fillna("")
    df.columns = [c.strip().lower() for c in df.columns]
    
    print(f"📊 원본 데이터: {len(df)}개")
    
    # 필요한 컬럼만 선택
    df = df[["raw_name", "standard_substance_id"]]
    
    # NaN 값 제거
    df = df.dropna()
    print(f"📊 NaN 제거 후: {len(df)}개")
    
    # 빈 문자열 제거
    df = df[df["raw_name"].str.strip() != ""]
    df = df[df["standard_substance_id"].str.strip() != ""]
    print(f"📊 빈 문자열 제거 후: {len(df)}개")
    
    # 중복 제거
    df = df.drop_duplicates()
    print(f"📊 중복 제거 후: {len(df)}개")
    
    # 결과 저장
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ 정리된 데이터 저장: {OUTPUT_CSV}")
    
    # 통계 출력
    print(f"\n📈 정리 결과:")
    print(f"  제거된 행: {len(pd.read_csv(INPUT_CSV)) - len(df)}개")
    print(f"  최종 평가 데이터: {len(df)}개")
    
    return df

if __name__ == "__main__":
    clean_evaluation_data()
