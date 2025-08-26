# LLM Service

로컬에서 LLM 모델을 훈련하고 추론할 수 있는 LangChain 기반 서비스입니다.

## 주요 기능

### 1. 모델 관리
- 모델 등록, 조회, 활성화/비활성화, 삭제
- 모델 유효성 검사
- 모델 통계 정보 제공

### 2. 모델 훈련
- 비동기 훈련 작업 관리
- 훈련 진행률 실시간 모니터링
- 훈련 작업 취소 및 삭제
- 다양한 데이터 형식 지원 (JSON, CSV)

### 3. LLM 추론
- 실시간 채팅 추론
- 모델 동적 로드/언로드
- 대화 컨텍스트 지원
- 생성 파라미터 조정 (temperature, top_p 등)

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **LangChain**: LLM 프레임워크
- **Transformers**: Hugging Face 모델 라이브러리
- **PyTorch**: 딥러닝 프레임워크
- **SQLAlchemy**: ORM
- **SQLite/PostgreSQL**: 데이터베이스

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
DATABASE_URL=sqlite:///./llm_service.db
USE_GPU=false
MODEL_CACHE_DIR=./models
TRAINING_DATA_DIR=./data
HF_TOKEN=your_huggingface_token
```

### 3. 서비스 실행
```bash
python -m app.main
```

서비스는 기본적으로 `http://localhost:8005`에서 실행됩니다.

## API 엔드포인트

### LLM 추론 API
- `POST /api/v1/llm/chat`: 채팅 추론
- `GET /api/v1/llm/models/loaded`: 로드된 모델 목록
- `POST /api/v1/llm/models/{model_name}/unload`: 모델 언로드

### 훈련 API
- `POST /api/v1/training/start`: 훈련 작업 시작
- `GET /api/v1/training/status/{job_id}`: 훈련 상태 조회
- `POST /api/v1/training/cancel/{job_id}`: 훈련 작업 취소
- `GET /api/v1/training/jobs`: 모든 훈련 작업 목록

### 모델 관리 API
- `POST /api/v1/model/register`: 모델 등록
- `GET /api/v1/model/list`: 모든 모델 목록
- `GET /api/v1/model/active`: 활성 모델 목록
- `PUT /api/v1/model/{model_name}/activate`: 모델 활성화
- `DELETE /api/v1/model/{model_name}`: 모델 삭제

## 사용 예시

### 1. 모델 등록
```python
import requests

model_info = {
    "name": "my-custom-model",
    "version": "1.0.0",
    "model_type": "gpt",
    "base_model": "microsoft/DialoGPT-medium",
    "model_path": "./models/my-custom-model",
    "description": "내가 훈련한 커스텀 모델"
}

response = requests.post("http://localhost:8005/api/v1/model/register", json=model_info)
```

### 2. 채팅 추론
```python
chat_request = {
    "message": "안녕하세요!",
    "model_name": "my-custom-model",
    "max_length": 100,
    "temperature": 0.7
}

response = requests.post("http://localhost:8005/api/v1/llm/chat", json=chat_request)
print(response.json()["response"])
```

### 3. 모델 훈련
```python
training_request = {
    "model_name": "my-finetuned-model",
    "base_model": "microsoft/DialoGPT-medium",
    "data_path": "./data/training_data.json",
    "output_path": "./models/my-finetuned-model",
    "training_config": {
        "num_epochs": 3,
        "batch_size": 4,
        "learning_rate": 5e-5,
        "max_length": 512,
        "text_column": "text"
    }
}

response = requests.post("http://localhost:8005/api/v1/training/start", json=training_request)
job_id = response.json()["job_id"]
```

## 데이터 형식

### 훈련 데이터 (JSON)
```json
[
    {
        "text": "사용자: 안녕하세요\n어시스턴트: 안녕하세요! 무엇을 도와드릴까요?"
    },
    {
        "text": "사용자: 날씨가 어때요?\n어시스턴트: 오늘은 맑고 화창한 날씨입니다."
    }
]
```

### 훈련 데이터 (CSV)
```csv
text
"사용자: 안녕하세요\n어시스턴트: 안녕하세요! 무엇을 도와드릴까요?"
"사용자: 날씨가 어때요?\n어시스턴트: 오늘은 맑고 화창한 날씨입니다."
```

## Docker 실행

```bash
# 이미지 빌드
docker build -t llm-service .

# 컨테이너 실행
docker run -p 8005:8005 -v $(pwd)/models:/app/models -v $(pwd)/data:/app/data llm-service
```

## 주의사항

1. **GPU 사용**: GPU를 사용하려면 `USE_GPU=true`로 설정하고 CUDA가 설치되어 있어야 합니다.
2. **메모리 관리**: 대용량 모델 사용 시 충분한 메모리가 필요합니다.
3. **모델 저장**: 훈련된 모델은 `MODEL_CACHE_DIR`에 저장됩니다.
4. **데이터 백업**: 중요한 훈련 데이터는 별도로 백업하세요.

## 라이센스

MIT License
