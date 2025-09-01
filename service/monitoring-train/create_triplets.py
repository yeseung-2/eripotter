#!/usr/bin/env python3
"""
개선된 PAIR → Triplet 변환
1. 실제 매핑 관계 기반 Positive 선택
2. 유사하지만 다른 물질들을 Negative로 선택
3. 더 많은 triplet 생성
"""

import pandas as pd
import numpy as np
import random
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict

# 파일 경로 설정
REG_XLSX = "./data/reg_test1.xlsx"
PAIR_CSV = "./data/training_pairs_from_reg_hard5_typos3 (1).csv"
OUTPUT_TRAIN = "./data/triplets_train_improved.jsonl"
OUTPUT_DEV = "./data/triplets_dev_improved.jsonl"

def load_data():
    """데이터 로드"""
    print("📊 데이터 로드 중...")
    
    # 규정 데이터
    reg = pd.read_excel(REG_XLSX).fillna("")
    reg.columns = [c.strip().lower() for c in reg.columns]
    reg = reg[["sid", "name"]].drop_duplicates()
    
    # 훈련 쌍 데이터 (실제 매핑 관계)
    pair = pd.read_csv(PAIR_CSV).fillna("")
    pair.columns = [c.strip().lower() for c in pair.columns]
    pair = pair[["raw_name", "standard_substance_id"]].drop_duplicates()
    
    print(f"규정 데이터: {len(reg)}개")
    print(f"훈련 쌍 데이터: {len(pair)}개")
    
    return reg, pair

def build_synonym_groups(reg: pd.DataFrame, pair: pd.DataFrame):
    """동의어 그룹 구축"""
    print("🔄 동의어 그룹 구축 중...")
    
    # SID별로 모든 이름 수집
    sid_to_names = defaultdict(set)
    
    # 규정 데이터에서 이름 수집
    for _, row in reg.iterrows():
        sid = row["sid"]
        name = row["name"].strip()
        
        # 데이터 품질 검증
        if (sid and len(str(sid).strip()) > 0 and 
            name and len(name) > 0 and 
            name.lower() != "nan" and 
            not name.startswith("nan")):
            sid_to_names[sid].add(name)
    
    # 매핑 관계에서도 이름 추가
    for _, row in pair.iterrows():
        raw_name = row["raw_name"].strip()
        sid = row["standard_substance_id"]
        
        # 데이터 품질 검증
        if (sid and len(str(sid).strip()) > 0 and 
            raw_name and len(raw_name) > 0 and 
            raw_name.lower() != "nan" and 
            not raw_name.startswith("nan")):
            sid_to_names[sid].add(raw_name)
    
    # 동의어 그룹 생성 (유효한 SID만)
    synonym_groups = {}
    for sid, names in sid_to_names.items():
        if len(names) > 0 and sid and len(str(sid).strip()) > 0:
            # 추가 필터링: 빈 문자열이나 nan 제거
            valid_names = [name for name in names 
                         if name and len(name.strip()) > 0 
                         and name.lower() != "nan" 
                         and not name.startswith("nan")]
            if valid_names:
                synonym_groups[sid] = valid_names
    
    print(f"동의어 그룹: {len(synonym_groups)}개")
    
    # 그룹 크기별 통계
    group_sizes = [len(names) for names in synonym_groups.values()]
    print(f"평균 그룹 크기: {np.mean(group_sizes):.1f}")
    print(f"최대 그룹 크기: {max(group_sizes)}")
    print(f"최소 그룹 크기: {min(group_sizes)}")
    
    return synonym_groups

def find_similar_substances(synonym_groups: Dict[str, List[str]]):
    """유사한 물질들 찾기 (같은 카테고리 내에서)"""
    print("🔄 유사 물질 그룹 구축 중...")
    
    # SID에서 카테고리 추출 (예: GHG-HFCs, APE-VOC 등)
    category_to_sids = defaultdict(list)
    for sid in synonym_groups.keys():
        if '__' in sid:
            category = sid.split('__')[0]
            category_to_sids[category].append(sid)
    
    # 같은 카테고리 내에서 유사한 물질들 찾기
    similar_groups = {}
    for category, sids in category_to_sids.items():
        if len(sids) > 1:
            similar_groups[category] = sids
    
    print(f"유사 물질 그룹: {len(similar_groups)}개")
    return similar_groups

def create_improved_triplets(synonym_groups: Dict[str, List[str]], 
                           similar_groups: Dict[str, List[str]],
                           train_ratio: float = 0.8, 
                           max_triplets_per_anchor: int = 30):
    """개선된 Triplet 생성"""
    print(f"\n🔄 개선된 Triplet 생성 중... (훈련 비율: {train_ratio*100}%)")
    
    all_sids = list(synonym_groups.keys())
    
    # 훈련/개발 분할
    random.shuffle(all_sids)
    split_idx = int(len(all_sids) * train_ratio)
    train_sids = all_sids[:split_idx]
    dev_sids = all_sids[split_idx:]
    
    print(f"훈련 SID: {len(train_sids)}개")
    print(f"개발 SID: {len(dev_sids)}개")
    
    def generate_improved_triplets_for_sids(sids: List[str], max_per_anchor: int = 30):
        triplets = []
        
        for sid in sids:
            names = synonym_groups[sid]
            if len(names) < 1:
                continue
            

            
            # 카테고리 추출
            category = sid.split('__')[0] if '__' in sid else 'unknown'
            
            # 같은 카테고리의 다른 SID들 (유사한 물질들)
            similar_sids = similar_groups.get(category, [])
            similar_sids = [s for s in similar_sids if s != sid]
            
            # 다른 카테고리의 SID들 (다른 물질들)
            other_sids = [s for s in all_sids if s not in similar_sids and s != sid]
            
            for i in range(min(len(names), max_per_anchor)):
                anchor = names[i]
                
                # Positive 선택 전략:
                # 1. 같은 SID의 다른 이름 (가장 확실한 동의어)
                # 2. 같은 카테고리의 다른 SID 이름 (유사한 물질)
                positive_candidates = []
                
                # 1. 같은 SID의 다른 이름
                same_sid_names = [n for n in names if n != anchor and n.strip()]
                positive_candidates.extend(same_sid_names)
                
                # 2. 같은 카테고리의 다른 SID 이름 (가중치 낮게)
                if similar_sids:
                    for similar_sid in random.sample(similar_sids, min(3, len(similar_sids))):
                        similar_names = synonym_groups[similar_sid]
                        positive_candidates.extend(similar_names)
                
                # Positive 선택
                if positive_candidates:
                    positive = random.choice(positive_candidates)
                else:
                    continue
                
                # Negative 선택 전략:
                # 1. 다른 카테고리의 물질들 (가장 확실한 다른 물질)
                # 2. 같은 카테고리지만 다른 SID (유사하지만 다른 물질)
                negative_candidates = []
                
                # 1. 다른 카테고리의 물질들
                if other_sids:
                    for other_sid in random.sample(other_sids, min(5, len(other_sids))):
                        other_names = synonym_groups[other_sid]
                        negative_candidates.extend(other_names)
                
                # 2. 같은 카테고리의 다른 SID (가중치 낮게)
                if similar_sids:
                    for similar_sid in random.sample(similar_sids, min(2, len(similar_sids))):
                        similar_names = synonym_groups[similar_sid]
                        negative_candidates.extend(similar_names)
                
                # Negative 선택
                if negative_candidates:
                    negative = random.choice(negative_candidates)
                else:
                    continue
                
                # 데이터 품질 검증 강화
                if (not anchor.strip() or not positive.strip() or not negative.strip() or
                    anchor.lower() == "nan" or positive.lower() == "nan" or negative.lower() == "nan" or
                    anchor.startswith("nan") or positive.startswith("nan") or negative.startswith("nan")):
                    continue
                
                # negative의 실제 SID 찾기
                negative_sid = None
                for test_sid, test_names in synonym_groups.items():
                    if negative in test_names:
                        negative_sid = test_sid
                        break
                
                # positive의 실제 SID 찾기 (같은 SID가 아닌 경우)
                positive_sid = sid
                if positive not in names:  # 같은 SID에 없는 경우
                    for test_sid, test_names in synonym_groups.items():
                        if positive in test_names:
                            positive_sid = test_sid
                            break
                
                # SID 검증 - 모든 SID가 유효해야 함
                if not negative_sid or not positive_sid:
                    continue
                
                # 카테고리 검증
                if category == "unknown" or not category:
                    continue
                
                # Triplet 추가
                triplet = {
                    "anchor": anchor,
                    "positive": positive,
                    "negative": negative,
                    "anchor_sid": sid,
                    "positive_sid": positive_sid,
                    "negative_sid": negative_sid,
                    "category": category
                }
                triplets.append(triplet)
        
        return triplets
    
    # 훈련/개발 Triplet 생성
    train_triplets = generate_improved_triplets_for_sids(train_sids, max_triplets_per_anchor)
    dev_triplets = generate_improved_triplets_for_sids(dev_sids, max_triplets_per_anchor)
    
    print(f"훈련 Triplet: {len(train_triplets)}개")
    print(f"개발 Triplet: {len(dev_triplets)}개")
    
    return train_triplets, dev_triplets

def save_triplets(triplets: List[Dict], output_file: str):
    """Triplet 저장"""
    print(f"💾 Triplet 저장 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for triplet in triplets:
            f.write(json.dumps(triplet, ensure_ascii=False) + '\n')
    
    print(f"✅ 저장 완료: {len(triplets)}개")

def analyze_improved_triplets(train_triplets: List[Dict], dev_triplets: List[Dict]):
    """개선된 Triplet 분석"""
    print("\n📊 개선된 Triplet 분석...")
    
    # 카테고리별 분석
    train_categories = defaultdict(int)
    dev_categories = defaultdict(int)
    
    for t in train_triplets:
        train_categories[t["category"]] += 1
    
    for t in dev_triplets:
        dev_categories[t["category"]] += 1
    
    print("훈련 데이터 카테고리별 분포:")
    for category, count in sorted(train_categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count}개")
    
    print("개발 데이터 카테고리별 분포:")
    for category, count in sorted(dev_categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count}개")
    
    # 중복 확인
    train_anchors = set(t["anchor"] for t in train_triplets)
    dev_anchors = set(t["anchor"] for t in dev_triplets)
    overlap_anchors = train_anchors.intersection(dev_anchors)
    
    print(f"\n중복 확인:")
    print(f"  - Anchor 중복: {len(overlap_anchors)}개")
    
    if len(overlap_anchors) > 0:
        print("⚠️ Anchor 중복이 있습니다!")
    else:
        print("✅ Anchor가 완전히 분리되었습니다.")

def main():
    """메인 함수"""
    print("=" * 60)
    print("개선된 PAIR → Triplet 변환")
    print("=" * 60)
    
    # 1. 데이터 로드
    reg, pair = load_data()
    
    # 2. 동의어 그룹 구축
    synonym_groups = build_synonym_groups(reg, pair)
    
    # 3. 유사 물질 그룹 구축
    similar_groups = find_similar_substances(synonym_groups)
    
    # 4. 개선된 Triplet 생성
    train_triplets, dev_triplets = create_improved_triplets(
        synonym_groups, similar_groups, max_triplets_per_anchor=30
    )
    
    # 5. Triplet 분석
    analyze_improved_triplets(train_triplets, dev_triplets)
    
    # 6. 저장
    save_triplets(train_triplets, OUTPUT_TRAIN)
    save_triplets(dev_triplets, OUTPUT_DEV)
    
    # 7. 최종 요약
    print("\n" + "=" * 60)
    print("🎉 개선된 Triplet 생성 완료!")
    print("=" * 60)
    print(f"📁 훈련 데이터: {OUTPUT_TRAIN}")
    print(f"📁 개발 데이터: {OUTPUT_DEV}")
    print(f"📊 총 Triplet: {len(train_triplets) + len(dev_triplets)}개")
    print(f"📈 이전 대비 증가: {((len(train_triplets) + len(dev_triplets)) / 312 - 1) * 100:.1f}%")

if __name__ == "__main__":
    main()
