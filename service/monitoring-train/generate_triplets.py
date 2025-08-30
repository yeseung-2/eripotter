import pandas as pd, numpy as np, json
from pathlib import Path

PAIR_CSV = Path("data/training_pairs_from_reg_hard5_typos3 (1).csv")
OUT_TRAIN = Path("data/triplets_train_improved.jsonl")
OUT_DEV   = Path("data/triplets_dev_improved.jsonl")
np.random.seed(7)

pairs = pd.read_csv(PAIR_CSV).fillna("")
pairs.columns = [c.strip().lower() for c in pairs.columns]

# NaN 처리 개선: 같은 sid의 표준명 변형으로 채우기
def fill_nan_with_standard_variants(df):
    """NaN 값을 같은 sid의 표준명 변형으로 채우기"""
    # sid별로 표준명 수집
    sid_standards = {}
    for _, row in df.iterrows():
        sid = row['standard_substance_id']
        if pd.notna(row['standard_name']) and row['standard_name'].strip():
            if sid not in sid_standards:
                sid_standards[sid] = []
            sid_standards[sid].append(row['standard_name'].strip())
    
    # NaN 값을 같은 sid의 표준명으로 채우기
    for idx, row in df.iterrows():
        if pd.isna(row['raw_name']) or row['raw_name'].strip() == "":
            sid = row['standard_substance_id']
            if sid in sid_standards and sid_standards[sid]:
                # 같은 sid의 표준명 중 하나를 선택
                df.at[idx, 'raw_name'] = np.random.choice(sid_standards[sid])
            else:
                # 표준명이 없으면 제거
                df.at[idx, 'raw_name'] = None
    
    # NaN이 채워지지 않은 행 제거
    df = df.dropna(subset=['raw_name'])
    return df

# NaN 처리 적용
pairs = fill_nan_with_standard_variants(pairs)
pairs = pairs[["raw_name","standard_substance_id"]].drop_duplicates()

# sid 단위로 split (누수 방지)
sids = pairs["standard_substance_id"].unique().tolist()
np.random.shuffle(sids)
split = int(len(sids)*0.9)
train_sids, dev_sids = set(sids[:split]), set(sids[split:])

train = pairs[pairs["standard_substance_id"].isin(train_sids)]
dev   = pairs[pairs["standard_substance_id"].isin(dev_sids)]

def generate(df, negatives_per_anchor=2, max_anchors_per_sid=50):
    out=[]
    sid_list = sorted(df["standard_substance_id"].unique().tolist())
    for sid, g in df.groupby("standard_substance_id"):
        anchors = g["raw_name"].unique().tolist()[:max_anchors_per_sid]
        pos = sid  # 심플하게 sid를 Positive 텍스트로 사용
        for a in anchors:
            for _ in range(negatives_per_anchor):
                nsid = np.random.choice([s for s in sid_list if s!=sid])
                out.append({"anchor": a, "positive": pos, "negative": nsid})
    return out

for path,df in [(OUT_TRAIN,train),(OUT_DEV,dev)]:
    with path.open("w", encoding="utf-8") as f:
        for r in generate(df):
            f.write(json.dumps(r, ensure_ascii=False)+"\n")
    print("saved:", path)
