import pandas as pd, numpy as np, json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from difflib import SequenceMatcher

PAIR_CSV = Path("data/training_pairs_from_reg_hard5_typos3 (1).csv")
MODEL_DIR = "BAAI/bge-m3"
OUT_HARD_NEG = Path("data/hard_negatives.jsonl")

def load_model():
    """BGE-M3 모델 로딩"""
    print("🔄 BGE-M3 모델 로딩 중...")
    model = SentenceTransformer(MODEL_DIR)
    print("✅ 모델 로드 완료")
    return model

def create_faiss_index(model, substances):
    """물질명들을 임베딩하여 FAISS 인덱스 생성"""
    print("🔄 FAISS 인덱스 생성 중...")
    embeddings = model.encode(substances, show_progress_bar=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS 인덱스 생성 완료: {len(substances)}개 물질")
    return index, embeddings

def calculate_string_similarity(str1, str2):
    """문자열 유사도 계산 (n-gram 기반)"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def apply_chemical_rules(anchor_sid, candidate_sid):
    """화학적 규칙 적용 (동계열, 헤드 토큰 공유 등)"""
    anchor = anchor_sid.lower()
    candidate = candidate_sid.lower()
    
    # 1. 동계열 규칙 (가중치 높음)
    chemical_patterns = {
        'sulfate': 'sulfite',
        'sulfite': 'sulfate',
        'nitrate': 'nitrite', 
        'nitrite': 'nitrate',
        'phosphate': 'phosphite',
        'phosphite': 'phosphate',
        'chloride': 'chlorate',
        'chlorate': 'chloride',
        'sodium': 'potassium',
        'potassium': 'sodium',
        'acid': 'anhydride',
        'anhydride': 'acid',
        'acid': 'salt',
        'salt': 'acid'
    }
    
    # 동계열 확인
    for pattern, variant in chemical_patterns.items():
        if pattern in anchor and variant in candidate:
            return True, 2.0  # 높은 가중치
        elif variant in anchor and pattern in candidate:
            return True, 2.0
    
    # 2. 헤드 토큰 공유 확인
    anchor_words = anchor.split()
    candidate_words = candidate.split()
    
    if anchor_words and candidate_words:
        # 마지막 단어가 같으면 헤드 토큰 공유
        if anchor_words[-1] == candidate_words[-1]:
            return True, 1.5  # 중간 가중치
    
    # 3. n-gram 유사도 확인
    similarity = calculate_string_similarity(anchor, candidate)
    if similarity >= 0.6:
        return True, 1.0  # 기본 가중치
    
    return False, 0.0

def find_hard_negatives(model, index, substances, anchor_sid, gold_sid, top_k=100):
    """하드 네거티브 찾기 (개선된 버전)"""
    # 앵커 임베딩
    anchor_embedding = model.encode([anchor_sid], show_progress_bar=False)
    
    # Top-K 검색
    scores, indices = index.search(anchor_embedding.astype('float32'), top_k)
    
    hard_negatives = []
    pos_score = None
    
    # 정답 스코어 찾기
    for score, idx in zip(scores[0], indices[0]):
        if substances[idx] == gold_sid:
            pos_score = float(score)
            break
    
    for score, idx in zip(scores[0], indices[0]):
        candidate = substances[idx]
        neg_score = float(score)
        
        # 정답 제외
        if candidate == gold_sid:
            continue
        
        # 스코어 기준 필터링
        meets_score_criteria = False
        
        # 1. 절대 스코어 하한
        if neg_score >= 0.65:
            meets_score_criteria = True
        
        # 2. 경계부근 (pos_sim - neg_sim <= 0.05)
        if pos_score and (pos_score - neg_score) <= 0.05:
            meets_score_criteria = True
        
        if not meets_score_criteria:
            continue
        
        # 화학적 규칙 적용
        is_chemical_hard, weight = apply_chemical_rules(anchor_sid, candidate)
        
        if is_chemical_hard:
            # 화학적으로 어려운 케이스는 가중치 적용
            adjusted_score = neg_score * weight
            hard_negatives.append({
                'candidate': candidate,
                'score': neg_score,
                'adjusted_score': adjusted_score,
                'chemical_hard': True
            })
        else:
            # 일반적인 하드 네거티브
            hard_negatives.append({
                'candidate': candidate,
                'score': neg_score,
                'adjusted_score': neg_score,
                'chemical_hard': False
            })
    
    # 조정된 스코어로 정렬하고 상위 3-5개 선택
    hard_negatives = sorted(hard_negatives, key=lambda x: x['adjusted_score'], reverse=True)
    
    # 화학적으로 어려운 것 우선, 그 다음 일반적인 것
    chemical_hards = [n for n in hard_negatives if n['chemical_hard']]
    regular_hards = [n for n in hard_negatives if not n['chemical_hard']]
    
    selected = []
    # 화학적으로 어려운 것 2-3개
    selected.extend(chemical_hards[:3])
    # 일반적인 것 1-2개
    selected.extend(regular_hards[:2])
    
    return selected[:5]  # 최대 5개

def filter_meaningful_data(df):
    """의미있는 데이터만 필터링하는 함수"""
    # raw_name이 비어있거나 standard_substance_id가 비어있는 행 제거
    df = df.dropna(subset=['raw_name', 'standard_substance_id'])
    
    # raw_name이 비어있는 행 제거 (이 부분은 위에서 이미 처리되었으므로 중복 제거)
    df = df.dropna(subset=['raw_name'])
    
    
    return df

def main():
    # 데이터 로딩
    print("🔄 데이터 로딩 중...")
    pairs = pd.read_csv(PAIR_CSV).fillna("")
    pairs.columns = [c.strip().lower() for c in pairs.columns]
    
    # 의미있는 데이터만 필터링
    pairs = filter_meaningful_data(pairs)
    
    # 고유한 sid 목록 생성 (단순한 nan 제외)
    unique_sids = pairs['standard_substance_id'].unique().tolist()
    unique_sids = [sid for sid in unique_sids if sid and sid not in ["nan", "NaN", "NAN"]]
    print(f"✅ 총 {len(unique_sids)}개 고유 SID")
    
    # 모델 로딩
    model = load_model()
    
    # FAISS 인덱스 생성
    index, embeddings = create_faiss_index(model, unique_sids)
    
    # 하드 네거티브 생성
    print("🔄 하드 네거티브 생성 중...")
    hard_negatives = []
    
    for i, (_, row) in enumerate(pairs.iterrows()):
        if i % 100 == 0:
            print(f"진행률: {i}/{len(pairs)}")
        
        anchor_name = row['raw_name']
        gold_sid = row['standard_substance_id']
        
        # 유효성 검사 (단순한 nan만 제외)
        if not anchor_name or not gold_sid or gold_sid in ["nan", "NaN", "NAN"]:
            continue
        
        # 하드 네거티브 찾기
        negatives = find_hard_negatives(model, index, unique_sids, anchor_name, gold_sid, top_k=100)
        
        for neg in negatives:
            hard_negatives.append({
                'anchor_name': anchor_name,
                'anchor_sid': gold_sid,
                'negative_sid': neg['candidate'],
                'score': neg['score'],
                'chemical_hard': neg['chemical_hard']
            })
    
    # 결과 저장
    print("💾 하드 네거티브 저장 중...")
    with OUT_HARD_NEG.open("w", encoding="utf-8") as f:
        for neg in hard_negatives:
            f.write(json.dumps(neg, ensure_ascii=False) + "\n")
    
    print(f"✅ 하드 네거티브 생성 완료: {len(hard_negatives)}개")
    print(f"📁 저장 위치: {OUT_HARD_NEG}")
    
    # 통계 출력
    chemical_hards = sum(1 for n in hard_negatives if n['chemical_hard'])
    print(f"📊 화학적 하드 네거티브: {chemical_hards}개 ({chemical_hards/len(hard_negatives)*100:.1f}%)")

if __name__ == "__main__":
    main()
