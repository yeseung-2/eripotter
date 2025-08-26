# app/utils/jsonl_logger.py
from __future__ import annotations
import os, json, time, uuid, threading

class JsonlLogger:
    """
    Append-only JSONL 로거 (동기 방식, 파일 회전 지원).
    - FastAPI 동기 핸들러(def)에서도 안전하게 사용 가능
    - 한 줄 = 한 레코드 (NDJSON)
    """
    def __init__(self, path: str, rotate_mb: int = 200):
        self.path = path
        self.rotate_bytes = rotate_mb * 1024 * 1024
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def _need_rotate(self) -> bool:
        return os.path.exists(self.path) and os.path.getsize(self.path) >= self.rotate_bytes

    def _rotate(self) -> None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        base, ext = os.path.splitext(self.path)
        os.replace(self.path, f"{base}.{ts}{ext or '.jsonl'}")

    def log(self, record: dict) -> None:
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            if self._need_rotate():
                self._rotate()
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def log_qa(self, *, question: str, answer: str, retrieved_chunks=None, citations=None, meta=None) -> None:
        rec = {
            "qid": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "input": question,
            "output": answer,
            "retrieved_chunks": retrieved_chunks or [],
            "citations": citations or [],
            "meta": meta or {},
        }
        self.log(rec)
