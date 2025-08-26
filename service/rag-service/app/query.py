from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple
from pathlib import Path
import os, re
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .config import LLM_BACKEND, BASE_MODEL, OPENAI_API_KEY
from .vectorstore import retriever, collection_path
from .utils.jsonl_logger import JsonlLogger

_LLM = None

def get_llm():
    """
    HF 로컬(예: Polyglot 3.8B) 또는 OpenAI 백엔드.
    윈도우 환경 안정화를 위해 device_map 미사용, 단일 GPU로 지정.
    """
    global _LLM
    if _LLM is not None:
        return _LLM

    if LLM_BACKEND == "openai":
        from langchain_openai import ChatOpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 미설정")
        _LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        return _LLM

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_community.llms import HuggingFacePipeline

    try:
        torch.set_float32_matmul_precision("high")
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    except Exception:
        pass

    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token

    device = 0 if torch.cuda.is_available() else -1

    mdl = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype="auto",
    )
    if device >= 0:
        mdl = mdl.to("cuda")

    gen = pipeline(
        "text-generation",
        model=mdl,
        tokenizer=tok,
        max_new_tokens=256,
        min_new_tokens=32,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.05,
        return_full_text=False,
        pad_token_id=tok.eos_token_id,
        device=device,
    )

    _LLM = HuggingFacePipeline(pipeline=gen)
    return _LLM


# ------ Prompt ------

PROMPT = PromptTemplate.from_template(
"""역할: 당신은 RAG 파이프라인에 주어진 지속가능경영보고서(SOURCES)만을 근거로, 요청된 업종/지표에 맞는 ESG 개선 활동을 벤치마킹하여 간결한 실행안을 제시하는 분석가다.

목표: [질문]에 명시된 업종/지표(GRI)에 부합하는 실제 사례 문장만을 근거로,
<p>활동:</p><p>방법:</p><p>목표:</p> 세 줄의 HTML을 한국어로 생성한다.

준수 규칙:
- 반드시 [SOURCES] 안의 문장만 사용. 자료 밖 추론/가정 금지.
- 본문에 URL/파일명/페이지 등 메타데이터 노출 금지.
- 각 줄 끝은 반드시 근거 번호 [n]로 마무리 (예: …[1])
- 가능하면 각 줄에 1문장 직접 인용 포함(원문은 「」로 감싸기).
- 근거가 부족하면 해당 줄은 INSUFFICIENT_EVIDENCE 로만 출력.
- 숫자/단위/지표 명칭은 원문을 우선하며 불필요한 각색 금지.

업종/지표 정합성:
- 우선순위 1. 질문 업종과 완전 일치 2. 유사 업종(동일 GICS 대·중분류) 3. 그래도 없으면 INSUFFICIENT_EVIDENCE.
- 질문에 기재된 GRI 코드와 직접 관련된 문장만 사용(예: 302-1/3/4는 에너지 사용/집약도/감축 활동, 403-2/9는 재해 예방/재해율·LTIFR 등).

작성 절차(내부 사고 지시):
1) [SOURCES]를 훑어 업종/지표가 맞는 문장만 선별한다(회사명/연도/업종 라벨은 판단에만 사용, 본문 노출 금지).
2) 선별 문장에서 실행 요소를 추출해 ‘활동/방법/목표’에 1문장씩 배치하고, 각 줄 끝에 해당 근거의 [번호]를 붙인다.
3) 직접 인용이 가능하면 1곳 이상 「원문」을 그대로 삽입한다.
4) 한 줄이라도 근거가 부족하면 그 줄은 INSUFFICIENT_EVIDENCE로만 출력한다.
5) 최종 포맷 유효성 확인: 정확히 3개의 <p> 줄, 각 줄 끝 [n], 메타데이터 미노출.

출력 형식(정확히 준수):
<p>활동: …[n]</p><p>방법: …[n]</p><p>목표: …[n]</p>

[형식 예시 — 포맷만 참고, 내용/회사/지표와 무관]
질문: 네이버의 지속가능경영보고서에서 산업재해율을 저감하기 위한 ESG 활동 사례를 찾아줘. 산업재해율에 관련된 내용은 GRI 403-2, 403-9에 해당해.
응답: <p>활동: 임차 데이터센터 에너지 효율 개선</p><p>방법: 공조 환경 개선, 액침 냉각 기술에 대한 PoC 실시 및 성능·효율성 테스트, 표준 사양서 및 기술 기준 수립</p><p>목표: 에너지 절감 및 온실가스 감축</p>

질문: 무림의 지속가능경영보고서에서 조직내 에너지 사용량을 저감하기 위한 ESG 활동 사례를 찾아줘. 조직내 에너지 사용량에 관련된 내용은 GRI 302-1, 302-3, 302-4에 해당해.
응답: <p>활동: 산업재해 발생 유형별 예방 대책 수립</p><p>방법: 10대 사고 유형 도출 및 맞춤형 교육·관리 시행</p><p>목표: 반복 재해 방지 및 사고 감소</p>

질문: 포스코퓨처엠의 지속가능경영보고서에서 윤리헌장 및 실천 규범을 갖추기 위한 ESG 활동 사례를 찾아줘. 윤리헌장 및 실천 규범을 갖추기 위해서는 경영자가 윤리경영의지를 발표하고, 윤리경영 실천을 위한 계획을 수립하고 규범을 갖추고, 윤리/인권/경영투명성 등의 임직원 교육을 정기적으로 실시하고, 기업의 의사결정 과정에 준법 및 윤리성을 점검할 수 있는 체계와 조직을 갖추고, 윤리경영 방침 및 결과를 문서화하여 대내외적으로 공개해야 하고, 이와 관련된 내용을 찾아주면 돼. 윤리헌장 및 실천 규범에 관련된 내용은 GRI 302-1, 302-3, 302-4에 해당해.
응답: <p>활동: 인권침해 고충처리 채널 운영</p><p>방법: 윤리경영 웹사이트를 통한 신고채널 운영, 제보자 보호 및 신속한 조사 절차 수립</p><p>목표: 인권침해 예방 및 대응 체계 강화</p>
[형식 예시 끝 — 위 예시는 ‘출력 형태’만 보여주며, 실제 생성에는 절대 사용하지 말 것]

[질문]
{question}

[SOURCES]
{sources}
# 포맷 예: [1] 회사명, 연도, (업종: 제지) — 「발췌문 1~2문장」 + 보조 요약
"""
)


router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryReq(BaseModel):
    question: str
    top_k: int = 5
    # 기본 컬렉션: 환경변수 우선 → 없으면 통일된 기본값 사용
    collections: List[str] = [
        os.getenv("SR_COLLECTION", "sustainability_reports"),
        os.getenv("STD_COLLECTION", "standards"),
    ]

_qa_logger = JsonlLogger(
    path=os.getenv("QA_JSONL_PATH", "./data/logs/qa_runs.jsonl"),
    rotate_mb=int(os.getenv("QA_JSONL_ROTATE_MB", "200")),
)

def _dedup_docs(docs: List[Document]) -> List[Document]:
    seen: Set[Tuple[str, str]] = set()
    uniq: List[Document] = []
    for d in docs:
        m = d.metadata or {}
        key = (str(m.get("source")), str(m.get("page_from")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(d)
    return uniq


# ---- 프롬프트 길이 컷팅 ----
from transformers import AutoTokenizer as _AutoTokForLen
_tok4len = None
def _get_len_tokenizer():
    global _tok4len
    if _tok4len is None:
        _tok4len = _AutoTokForLen.from_pretrained(BASE_MODEL, use_fast=True)
    return _tok4len

MAX_CTX = 2048
RESERVED = 256
def fit_prompt(tokenizer, text, max_len=MAX_CTX-RESERVED):
    ids = tokenizer(text, return_tensors="pt").input_ids[0]
    if len(ids) <= max_len:
        return text
    keep_ids = ids[-max_len:]
    return tokenizer.decode(keep_ids, skip_special_tokens=True)


_CITE_RE = re.compile(r"\[\d+\]")

@router.post("/query")
def query(req: QueryReq):
    # 1) 컬렉션 경로 확인
    paths = []
    for c in req.collections:
        p = collection_path(c)
        if not ((p / "index.faiss").exists() and (p / "index.pkl").exists()):
            raise HTTPException(404, f"FAISS 인덱스가 없습니다: {p}")
        paths.append(p)

    # 2) 컬렉션별 검색
    k = max(1, req.top_k)
    per = max(1, k // len(paths))
    docs: List[Document] = []
    for p in paths:
        r = retriever(p, k=per)
        docs.extend(r.invoke(req.question))
    docs = _dedup_docs(docs)

    if len(docs) < k:
        r0 = retriever(paths[0], k=k)
        extra = _dedup_docs(r0.invoke(req.question))
        have = {(str(d.metadata.get("source")), str(d.metadata.get("page_from"))) for d in docs}
        for d in extra:
            key = (str(d.metadata.get("source")), str(d.metadata.get("page_from")))
            if key not in have:
                docs.append(d)
                have.add(key)
            if len(docs) >= k:
                break
    docs = docs[:k]

    # 3) SOURCES 목록 구성 (번호매김)
    def brief(txt: str, n=160):
        s = (txt or "").strip().replace("\n", " ")
        return (s[:n] + "…") if len(s) > n else s

    src_lines = []
    for i, d in enumerate(docs, start=1):
        m = d.metadata or {}
        tag = f"[{i}] {m.get('company','?')} {m.get('year','?')} p.{m.get('page_from','?')}"
        src_lines.append(f"{tag}: {brief(d.page_content)}")
    sources_block = "\n".join(src_lines) if src_lines else "(no sources)"

    # 4) 프롬프트 생성 + 길이 컷
    llm = get_llm()
    prompt = PROMPT.format(question=req.question, sources=sources_block)
    prompt = fit_prompt(_get_len_tokenizer(), prompt)

    # 5) 생성
    answer = llm.invoke(prompt)
    text = (str(answer) or "").strip()

    # 6) 로깅 품질 가드
    insufficient = "INSUFFICIENT_EVIDENCE" in text.upper()
    has_cite = bool(_CITE_RE.search(text))

    # 참고 메타
    refs: List[Dict] = []
    for idx, d in enumerate(docs, start=1):
        m = d.metadata or {}
        refs.append({
            "idx": idx,
            "source": m.get("source"),
            "company": m.get("company"),
            "year": m.get("year"),
            "page_from": m.get("page_from"),
            "page_to": m.get("page_to"),
            "collection": m.get("collection"),
        })

    # 7) JSONL 로그 (근거 미흡/인용 없음이면 스킵)
    if not insufficient and has_cite:
        try:
            retrieved_chunks = []
            for d in docs:
                m = d.metadata or {}
                snippet = brief(d.page_content, 300)
                retrieved_chunks.append({
                    "source": m.get("source"),
                    "company": m.get("company"),
                    "year": m.get("year"),
                    "page_from": m.get("page_from"),
                    "page_to": m.get("page_to"),
                    "collection": m.get("collection"),
                    "text": snippet,
                })
            _qa_logger.log_qa(
                question=req.question,
                answer=text,
                retrieved_chunks=retrieved_chunks,
                citations=refs,
                meta={"route": "/rag/query", "top_k": req.top_k, "collections": req.collections},
            )
        except Exception:
            pass

    # 8) 사용자 응답 (근거 부족 시 안내)
    if insufficient or not has_cite:
        return {
            "answer": "제공된 컨텍스트로 답을 확정하기 어렵습니다. 질문을 더 구체화하거나, top_k를 늘리거나, 관련 문서 범위를 확장해 주세요.",
            "refs": refs
        }
    return {"answer": text, "refs": refs}
