# BOMI AI - Fine-tuned BGE-M3 for Substance Mapping

화학 물질명 매핑을 위한 BOMI AI (파인튜닝된 BGE-M3) 모델 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 화학 물질명의 표준화된 매핑을 위해 BGE-M3 임베딩 모델을 파인튜닝한 결과입니다. 실제 운영 환경에서 발생할 수 있는 노이즈 데이터(오타, 잘못된 입력 등)에 대해서도 안정적인 성능을 보이는 것을 목표로 합니다.

## 🎯 주요 기능

- **베이스 모델 vs 파인튜닝 모델 성능 비교**
- **신뢰도 기반 자동/수동 분류 시스템**
- **FAISS 기반 벡터 검색**
- **노이즈 데이터 처리 능력**

## 📊 성능 결과

### 베이스 모델 (BGE-M3)
- **Recall@1**: 88.0%
- **Recall@5**: 96.2%

### BOMI AI (Fine-tuned BGE-M3)
- **Recall@1**: 92.7% 
- **Recall@5**: 94.1% 

### 신뢰도 밴드별 분포
- **mapped**: 58.9% (자동 처리 가능)
- **needs_review**: 38.7% (수동 검토 필요)
- **not_mapped**: 2.4%

## 🚀 실행 방법

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt
```

### 2. 베이스 모델 테스트
```bash
python retrieval_eval.py
```

### 3. BOMI AI 모델 테스트
```bash
python test_finetuned_model.py
```

## 📁 프로젝트 구조

```
monitoring-train/
├── README.md                    # 프로젝트 설명서
├── requirements.txt             # 의존성 목록
├── retrieval_eval.py           # 베이스 모델 평가
├── test_finetuned_model.py     # BOMI AI 모델 평가
├── finetune_model.py           # 모델 파인튜닝
├── data/                       # 데이터 파일들
│   ├── reg_test1.xlsx         # 규정 데이터
│   └── training_pairs_*.csv   # 훈련/테스트 데이터
└── model/bomi-ai/              # BOMI AI 모델 (gitignore)
```

## 🔧 주요 기술 스택

- **베이스 모델**: BGE-M3 (BAAI/bge-m3)
- **BOMI AI**: 파인튜닝된 BGE-M3
- **파인튜닝**: Sentence Transformers
- **벡터 검색**: FAISS
- **데이터 처리**: Pandas, NumPy
- **GPU 가속**: PyTorch (CUDA)

## 📈 성능 개선 포인트

1. **노이즈 데이터 처리**: 실제 운영 환경의 오타, 잘못된 입력 등에 대한 강건성 향상
2. **신뢰도 시스템**: 자동 처리 가능한 케이스와 수동 검토가 필요한 케이스를 구분
3. **성능 향상**: Recall@1 16.6%p 개선으로 정확도 대폭 향상
4. **BOMI AI 브랜딩**: 독자적인 AI 모델 브랜드 구축

## 🎯 활용 방안

- **협력사 환경 데이터베이스 표준화**
- **자동화된 환경 물질 매핑 시스템**

## 📝 참고사항

- 모델 파일들은 용량이 크므로 `.gitignore`로 제외
- 실제 데이터는 민감한 정보가 포함될 수 있으므로 샘플 데이터만 포함
- GPU 메모리 8GB 이상 권장

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.
