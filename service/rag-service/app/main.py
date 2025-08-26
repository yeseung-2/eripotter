from fastapi import FastAPI
from .query import router as rag_router
from .ingest import router as ingest_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="RAG Service (FAISS + LangChain)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라면 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"ok": True}

app.include_router(rag_router)
app.include_router(ingest_router)
