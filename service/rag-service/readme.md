rag_faiss.py 하나에

PDF 로더

텍스트 분할기

임베딩 생성

FAISS upsert

main() 실행

이 전부 들어 있음 → 단순 실행용 스크립트

2. 서비스화할 때 권장 분리 (여러 파일)

아까 제가 나눠드린 구조는 다음과 같이 역할을 나눠요:

app/config.py → 경로, 환경변수, 설정

app/embeddings.py → HuggingFace 임베딩 모델 로딩

app/vectorstore.py → FAISS 로딩/저장 함수

app/ingest.py → PDF를 읽고 split→embedding→FAISS upsert 실행하는 API

app/query.py → 질문을 받아서 retriever→LLM→답변 API

app/main.py → FastAPI 엔트리포인트 (uvicorn 실행 대상)

즉, 지금 올려주신 단일 스크립트의 코드들을 위 역할별로 잘라 넣은 거예요.

extract_company_year, load_pdf_dir, split_docs, upsert_faiss 같은 함수들은 → ingest.py 쪽

RecursiveCharacterTextSplitter, HuggingFaceEmbeddings 로딩 부분은 → embeddings.py

main() 로직(build_collection)은 → CLI 실행 시만 쓰거나 /ingest/pdfs API에서 호출