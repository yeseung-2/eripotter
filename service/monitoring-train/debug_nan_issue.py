import pandas as pd
import numpy as np
import json
from pathlib import Path

def debug_nan_issue():
    """JSONL 변환 과정에서 nan이 어떻게 생성되었는지 디버깅합니다."""
    
    # 1. 원본 CSV 파일 확인
    csv_path = Path("data/training_pairs_test1_noised_v1.csv")
    
    if not csv_path.exists():
        print("❌ CSV 파일을 찾을 수 없습니다.")
        return
    
    print("🔍 원본 CSV 파일 분석...")
    
    # CSV 파일을 다양한 방법으로 로드해서 비교
    print("\n1. 기본 로드:")
    df1 = pd.read_csv(csv_path)
    print(f"   데이터 타입: {df1.dtypes}")
    print(f"   빈 값 개수: {df1.isnull().sum()}")
    
    print("\n2. fillna('') 없이 로드:")
    df2 = pd.read_csv(csv_path, keep_default_na=True)
    print(f"   데이터 타입: {df2.dtypes}")
    print(f"   빈 값 개수: {df2.isnull().sum()}")
    
    print("\n3. fillna('') 적용:")
    df3 = pd.read_csv(csv_path).fillna("")
    print(f"   데이터 타입: {df3.dtypes}")
    print(f"   빈 값 개수: {df3.isnull().sum()}")
    
    # 4. raw_name 컬럼 상세 분석
    print(f"\n🔬 raw_name 컬럼 상세 분석:")
    
    # 원본 데이터에서 raw_name 확인
    raw_names = df1['raw_name'].dropna()
    print(f"  원본 raw_name 개수: {len(raw_names)}")
    
    # 고유값 확인
    unique_values = raw_names.unique()
    print(f"  고유값 개수: {len(unique_values)}")
    
    # "nan" 관련 값들 확인
    nan_like_values = [val for val in unique_values if str(val).lower() in ['nan', 'na', 'n/a', 'none', 'null']]
    print(f"  nan 관련 고유값: {nan_like_values}")
    
    # 5. 실제 "nan" 문자열 개수 확인
    actual_nan_count = (raw_names == "nan").sum()
    print(f"  실제 'nan' 문자열 개수: {actual_nan_count}")
    
    # 6. numpy.nan 개수 확인
    numpy_nan_count = raw_names.isna().sum()
    print(f"  numpy.nan 개수: {numpy_nan_count}")
    
    # 7. fillna 적용 후 확인
    filled_names = df1['raw_name'].fillna("")
    filled_nan_count = (filled_names == "nan").sum()
    print(f"  fillna 후 'nan' 문자열 개수: {filled_nan_count}")
    
    # 8. 샘플 데이터 출력
    print(f"\n📋 샘플 데이터:")
    print("원본 데이터 (처음 10개):")
    print(df1['raw_name'].head(10))
    
    print("\nfillna 적용 후 (처음 10개):")
    print(df1['raw_name'].fillna("").head(10))
    
    # 9. JSONL 변환 시뮬레이션
    print(f"\n🔄 JSONL 변환 시뮬레이션:")
    
    # 원본 데이터로 JSONL 변환
    jsonl_data_original = []
    for _, row in df1.iterrows():
        jsonl_data_original.append({
            'raw_name': row['raw_name'],
            'standard_substance_id': row['standard_substance_id'],
            'standard_substance_name': row['standard_substance_name']
        })
    
    # fillna 적용 후 JSONL 변환
    jsonl_data_filled = []
    for _, row in df1.iterrows():
        jsonl_data_filled.append({
            'raw_name': row['raw_name'] if pd.notna(row['raw_name']) else "",
            'standard_substance_id': row['standard_substance_id'] if pd.notna(row['standard_substance_id']) else "",
            'standard_substance_name': row['standard_substance_name'] if pd.notna(row['standard_substance_name']) else ""
        })
    
    # nan 개수 비교
    original_nan_count = sum(1 for item in jsonl_data_original if str(item['raw_name']).lower() == 'nan')
    filled_nan_count = sum(1 for item in jsonl_data_filled if str(item['raw_name']).lower() == 'nan')
    
    print(f"  원본 JSONL 변환 후 'nan' 개수: {original_nan_count}")
    print(f"  fillna 적용 후 JSONL 변환 'nan' 개수: {filled_nan_count}")
    
    # 10. 해결 방안 제시
    print(f"\n💡 해결 방안:")
    
    if original_nan_count > 0:
        print(f"  1. 원본 데이터에 실제 'nan' 문자열이 {original_nan_count}개 있습니다.")
        print(f"  2. 이는 데이터 수집 과정에서 발생한 것일 수 있습니다.")
    
    if numpy_nan_count > 0:
        print(f"  3. numpy.nan이 {numpy_nan_count}개 있습니다.")
        print(f"  4. fillna() 처리 시 빈 문자열로 변환됩니다.")
    
    print(f"  5. 권장사항: 원본 데이터에서 실제 결측값을 확인하고 적절히 처리하세요.")
    
    return df1

def fix_training_data():
    """학습 데이터를 수정합니다."""
    
    print("\n🔧 학습 데이터 수정...")
    
    # 원본 데이터 로드
    csv_path = Path("data/training_pairs_test1_noised_v1.csv")
    df = pd.read_csv(csv_path)
    
    # 실제 결측값만 처리 (numpy.nan)
    df_fixed = df.copy()
    df_fixed['raw_name'] = df_fixed['raw_name'].fillna("")
    df_fixed['standard_substance_id'] = df_fixed['standard_substance_id'].fillna("")
    df_fixed['standard_substance_name'] = df_fixed['standard_substance_name'].fillna("")
    
    # 빈 문자열을 가진 데이터 확인
    empty_raw_names = df_fixed[df_fixed['raw_name'] == ""]
    print(f"  빈 raw_name 개수: {len(empty_raw_names)}")
    
    # 실제 "nan" 문자열을 가진 데이터 확인
    actual_nan_names = df_fixed[df_fixed['raw_name'] == "nan"]
    print(f"  실제 'nan' 문자열 개수: {len(actual_nan_names)}")
    
    # 수정된 데이터 저장
    output_path = Path("data/training_pairs_fixed.csv")
    df_fixed.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"  수정된 데이터 저장: {output_path}")
    
    return df_fixed

if __name__ == "__main__":
    debug_nan_issue()
    fix_training_data()

