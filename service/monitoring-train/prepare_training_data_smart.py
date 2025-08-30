import pandas as pd
import numpy as np
import re
from pathlib import Path

def is_chemical_substance(text):
    """실제 화학물질명인지 판단합니다."""
    if pd.isna(text) or text == "":
        return False
    
    text_str = str(text).strip()
    
    # 1. 화학식 패턴 확인 (예: H2O, NaCl, C6H12O6)
    chemical_formula_pattern = r'^[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*$'
    if re.match(chemical_formula_pattern, text_str):
        return True
    
    # 2. 일반적인 화학물질명 패턴
    # - 숫자, 문자, 공백, 괄호, 하이픈, 슬래시 포함
    # - 최소 2글자 이상
    # - 단순한 결측값 패턴이 아님
    if len(text_str) >= 2:
        # 단순한 결측값 패턴 제외
        simple_nan_patterns = [
            "nan", "NaN", "NAN", "na", "NA", "n/a", "N/A", 
            "none", "None", "NONE", "unknown", "Unknown", "UNKNOWN",
            "미입력", "없음", "-", "—", "–", "null", "NULL"
        ]
        
        if text_str.lower() in [p.lower() for p in simple_nan_patterns]:
            return False
        
        # 괄호 안에 순도/규격 정보가 있는 경우 (예: NaN (99%))
        if re.search(r'\([^)]*%[^)]*\)', text_str):
            # 괄호 제거 후 다시 확인
            cleaned = re.sub(r'\([^)]*\)', '', text_str).strip()
            if cleaned.lower() in [p.lower() for p in simple_nan_patterns]:
                return False
        
        # 실제 화학물질명으로 보이는 패턴
        # - 알파벳과 숫자 조합
        # - 특수문자가 적절히 포함
        if re.search(r'[A-Za-z]', text_str):  # 알파벳 포함
            return True
    
    return False

def analyze_nan_patterns(data):
    """nan 패턴을 분석합니다."""
    nan_candidates = []
    chemical_substances = []
    
    for idx, row in data.iterrows():
        raw_name = row['raw_name']
        
        if pd.isna(raw_name) or raw_name == "":
            nan_candidates.append((idx, raw_name, "빈 값"))
            continue
        
        text_str = str(raw_name).strip()
        
        # 단순한 결측값 패턴
        simple_nan_patterns = [
            "nan", "NaN", "NAN", "na", "NA", "n/a", "N/A", 
            "none", "None", "NONE", "unknown", "Unknown", "UNKNOWN",
            "미입력", "없음", "-", "—", "–", "null", "NULL"
        ]
        
        if text_str.lower() in [p.lower() for p in simple_nan_patterns]:
            nan_candidates.append((idx, raw_name, "단순 결측값"))
        elif is_chemical_substance(raw_name):
            chemical_substances.append((idx, raw_name, "화학물질명"))
        else:
            # 애매한 케이스 - 추가 분석 필요
            nan_candidates.append((idx, raw_name, "애매한 케이스"))
    
    return nan_candidates, chemical_substances

def prepare_training_data_smart():
    """스마트한 방법으로 학습 데이터를 재구성합니다."""
    
    # 1. 기존 데이터 로드
    reg_path = Path("data/reg_test1.xlsx")
    pair_path = Path("data/training_pairs_test1_noised_v1.csv")
    
    if not reg_path.exists():
        print("❌ 규정 데이터 파일을 찾을 수 없습니다.")
        return
    
    if not pair_path.exists():
        print("❌ 훈련 쌍 데이터 파일을 찾을 수 없습니다.")
        return
    
    # 훈련 쌍 데이터 로드
    pair = pd.read_csv(pair_path).fillna("")
    
    print(f"📊 원본 데이터: {len(pair)}개")
    
    # 2. nan 패턴 분석
    print("\n🔍 nan 패턴 분석 중...")
    nan_candidates, chemical_substances = analyze_nan_patterns(pair)
    
    print(f"\n📋 분석 결과:")
    print(f"  nan 후보: {len(nan_candidates)}개")
    print(f"  화학물질명: {len(chemical_substances)}개")
    
    # 3. nan 후보들의 상세 분석
    print(f"\n🔬 nan 후보 상세 분석:")
    nan_by_type = {}
    for idx, text, reason in nan_candidates:
        if reason not in nan_by_type:
            nan_by_type[reason] = []
        nan_by_type[reason].append((idx, text))
    
    for reason, items in nan_by_type.items():
        print(f"  {reason}: {len(items)}개")
        if len(items) <= 5:  # 5개 이하면 모두 출력
            for idx, text in items:
                print(f"    - {text}")
        else:  # 5개 초과면 샘플만 출력
            for idx, text in items[:3]:
                print(f"    - {text}")
            print(f"    ... (총 {len(items)}개)")
    
    # 4. 사용자 확인
    print(f"\n❓ 처리 방법을 선택하세요:")
    print(f"  1. 모든 nan 후보를 UNMAPPED로 처리")
    print(f"  2. 단순 결측값만 UNMAPPED로 처리")
    print(f"  3. 수동으로 확인 후 처리")
    
    # 임시로 2번 선택 (단순 결측값만 처리)
    choice = 2
    
    if choice == 1:
        # 모든 nan 후보를 UNMAPPED로 처리
        nan_indices = [idx for idx, _, _ in nan_candidates]
        normal_indices = [idx for idx in range(len(pair)) if idx not in nan_indices]
    elif choice == 2:
        # 단순 결측값만 UNMAPPED로 처리
        nan_indices = [idx for idx, _, reason in nan_candidates if reason == "단순 결측값"]
        normal_indices = [idx for idx in range(len(pair)) if idx not in nan_indices]
    else:
        # 수동 확인 (임시로 2번과 동일하게 처리)
        nan_indices = [idx for idx, _, reason in nan_candidates if reason == "단순 결측값"]
        normal_indices = [idx for idx in range(len(pair)) if idx not in nan_indices]
    
    # 5. 데이터 분리
    nan_data = pair.iloc[nan_indices]
    normal_data = pair.iloc[normal_indices]
    
    print(f"\n✅ 최종 분류:")
    print(f"  정상 데이터: {len(normal_data)}개")
    print(f"  UNMAPPED 데이터: {len(nan_data)}개")
    
    # 6. 다운샘플링 (필요시)
    target_nan_ratio = 0.08
    max_nan_count = int(len(normal_data) * target_nan_ratio / (1 - target_nan_ratio))
    
    if len(nan_data) > max_nan_count:
        nan_data = nan_data.sample(n=max_nan_count, random_state=42)
        print(f"  다운샘플링된 UNMAPPED 데이터: {len(nan_data)}개")
    
    # 7. 새로운 학습 데이터 생성
    nan_training_data = []
    for _, row in nan_data.iterrows():
        nan_training_data.append({
            'raw_name': row['raw_name'],
            'standard_substance_id': '__UNMAPPED__',
            'standard_substance_name': '__UNMAPPED__',
            'is_unmapped': True
        })
    
    normal_training_data = []
    for _, row in normal_data.iterrows():
        normal_training_data.append({
            'raw_name': row['raw_name'],
            'standard_substance_id': row['standard_substance_id'],
            'standard_substance_name': row['standard_substance_name'],
            'is_unmapped': False
        })
    
    # 8. 데이터 합치기
    new_training_data = pd.DataFrame(normal_training_data + nan_training_data)
    
    print(f"\n🎯 최종 학습 데이터:")
    print(f"  총 데이터: {len(new_training_data)}개")
    print(f"  정상 데이터: {len(normal_training_data)}개")
    print(f"  UNMAPPED 데이터: {len(nan_training_data)}개")
    print(f"  UNMAPPED 비율: {len(nan_training_data)/len(new_training_data)*100:.1f}%")
    
    # 9. 파일 저장
    output_path = Path("data/training_pairs_smart_unmapped.csv")
    new_training_data.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 파일 저장 완료: {output_path}")
    
    return new_training_data

if __name__ == "__main__":
    prepare_training_data_smart()

