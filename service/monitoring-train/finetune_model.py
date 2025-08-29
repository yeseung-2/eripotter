from datasets import load_dataset
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
from pathlib import Path
import torch

MODEL_DIR   = "BAAI/bge-m3"  # 원본 BGE-M3 모델
TRAIN_PATH  = "data/triplets_train_improved.jsonl"
DEV_PATH    = "data/triplets_dev_improved.jsonl"
HARD_NEG_PATH = "data/hard_negatives.jsonl"
OUT_DIR     = "model/bomi-ai"  # BOMI AI 모델 저장 경로

def load_triplets(path):
    ds = load_dataset("json", data_files=path, split="train")
    ex=[]
    for r in ds:
        ex.append(InputExample(
            texts=[f"query: {r['anchor']}", f"passage: {r['positive']}", f"passage: {r['negative']}"]
        ))
    return ex

def load_hard_negatives(path):
    """하드 네거티브 로딩"""
    if not Path(path).exists():
        print(f"⚠️ 하드 네거티브 파일이 없습니다: {path}")
        return []
    
    ds = load_dataset("json", data_files=path, split="train")
    ex = []
    for r in ds:
        ex.append(InputExample(
            texts=[f"query: {r['anchor_name']}", f"passage: {r['negative_sid']}"]
        ))
    return ex

def create_mixed_batches(triplet_data, hard_neg_data, batch_size=64, mnrl_ratio=0.7):
    """MNRL 70% + Triplet 30% 비율로 배치 생성"""
    print("🔄 혼합 배치 생성 중...")
    
    # 배치 크기 계산
    mnrl_batch_size = int(batch_size * mnrl_ratio)
    triplet_batch_size = batch_size - mnrl_batch_size
    
    print(f"  MNRL 배치 크기: {mnrl_batch_size}")
    print(f"  Triplet 배치 크기: {triplet_batch_size}")
    
    # 데이터 로더 생성
    if hard_neg_data:
        mnrl_loader = DataLoader(hard_neg_data, batch_size=mnrl_batch_size, shuffle=True, drop_last=True)
        triplet_loader = DataLoader(triplet_data, batch_size=triplet_batch_size, shuffle=True, drop_last=True)
        return mnrl_loader, triplet_loader
    else:
        triplet_loader = DataLoader(triplet_data, batch_size=batch_size, shuffle=True, drop_last=True)
        return None, triplet_loader

print("🔄 BGE-M3 모델 로딩 중...")
model = SentenceTransformer(MODEL_DIR)
print("✅ 모델 로딩 완료")

print("🔄 학습 데이터 로딩 중...")
train_ex = load_triplets(TRAIN_PATH)
dev_ex   = load_triplets(DEV_PATH)
hard_neg_ex = load_hard_negatives(HARD_NEG_PATH)

print(f"✅ 학습 데이터: {len(train_ex)}개")
print(f"✅ 검증 데이터: {len(dev_ex)}개")
print(f"✅ 하드 네거티브: {len(hard_neg_ex)}개")

# 혼합 배치 생성
mnrl_loader, triplet_loader = create_mixed_batches(train_ex, hard_neg_ex, batch_size=64, mnrl_ratio=0.7)

# Loss 함수 설정
print("🔄 Loss 함수 설정 중...")

# 1. TripletLoss (margin=0.2)
triplet_loss = losses.TripletLoss(
    model, 
    distance_metric=losses.SiameseDistanceMetric.COSINE_DISTANCE, 
    triplet_margin=0.2
)

# 2. MultipleNegativesRankingLoss (하드 네거티브가 있을 때)
if mnrl_loader:
    mnr_loss = losses.MultipleNegativesRankingLoss(model)
    print("✅ MNRL 70% + Triplet 30% 비율로 학습")
else:
    print("✅ TripletLoss만 사용")

print("🚀 모델 fine-tuning 시작...")

# 하이퍼파라미터 설정
epochs = 3
warmup_steps = int(len(triplet_loader) * 0.1)  # 10% warmup

# 학습 실행
if mnrl_loader:
    # 하드 네거티브가 있으면 두 Loss 병행
    model.fit(
        train_objectives=[
            (mnrl_loader, mnr_loss),      # 70% MNRL
            (triplet_loader, triplet_loss)  # 30% Triplet
        ],
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={
            'lr': 2e-5,
            'weight_decay': 0.01
        },
        output_path=OUT_DIR
    )
else:
    # 하드 네거티브가 없으면 TripletLoss만
    model.fit(
        train_objectives=[(triplet_loader, triplet_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={
            'lr': 2e-5,
            'weight_decay': 0.01
        },
        output_path=OUT_DIR
    )

print("✅ Fine-tuning 완료!")
print("💾 모델 저장 위치:", OUT_DIR)
print(f"📊 학습 설정:")
print(f"  - 에포크: {epochs}")
print(f"  - 배치 크기: 64")
print(f"  - 학습률: 2e-5")
print(f"  - Weight Decay: 0.01")
print(f"  - Warmup: {warmup_steps} steps")
print(f"  - GPU 사용: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  - GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
