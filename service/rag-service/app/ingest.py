from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, DistanceStrategy
from langchain_community.document_loaders import PyPDFLoader
from .embeddings import embeddings
from .config import FAISS_DIR

router = APIRouter(prefix="/ingest", tags=["Ingest"])

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, chunk_overlap=150, separators=["\n## ", "\n#", "\n\n", "\n", " "],
)

class IngestReq(BaseModel):
    pdf_dir: str
    collection: str

@router.post("/pdfs")
def ingest_pdfs(req: IngestReq):
    src = Path(req.pdf_dir)
    if not src.exists():
        raise HTTPException(404, f"PDF 디렉토리가 없습니다: {src}")

    out = FAISS_DIR / req.collection
    out.mkdir(parents=True, exist_ok=True)

    docs = []
    for pdf in sorted(src.glob("*.pdf")):
        pages = PyPDFLoader(str(pdf)).load()
        for i, p in enumerate(pages, start=1):
            p.metadata.update({
                "collection": req.collection,
                "source": pdf.name,
                "page_from": i,
                "page_to": i,
            })
        docs.extend(pages)

    texts, metas = [], []
    for d in docs:
        for c in splitter.split_text(d.page_content or ""):
            c = c.strip()
            if c:
                texts.append(c)
                metas.append(dict(d.metadata))

    idx, pkl = out / "index.faiss", out / "index.pkl"
    if idx.exists() and pkl.exists():
        store = FAISS.load_local(
            str(out), embeddings, allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.COSINE
        )
        store.add_texts(texts, metadatas=metas)
        store.save_local(str(out))
        return {"status": "append", "chunks_added": len(texts), "collection": req.collection, "path": str(out)}
    else:
        store = FAISS.from_texts(
            texts, embeddings, metadatas=metas, distance_strategy=DistanceStrategy.COSINE
        )
        store.save_local(str(out))
        return {"status": "created", "chunks": len(texts), "collection": req.collection, "path": str(out)}
