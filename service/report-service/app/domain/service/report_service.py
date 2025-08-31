"""
Report Service - ESG 매뉴얼 기반 보고서 비즈니스 로직 처리 (LLM lazy 생성, 프록시 최신화, 임베딩 의존성 배제)
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..repository.report_repository import ReportRepository
from ..model.report_model import (
    ReportCreateRequest, ReportCreateResponse,
    ReportGetRequest, ReportGetResponse,
    ReportUpdateRequest, ReportUpdateResponse,
    ReportDeleteRequest, ReportDeleteResponse,
    ReportListResponse, ReportCompleteRequest, ReportCompleteResponse,
    IndicatorResponse, IndicatorListResponse, IndicatorInputFieldResponse, IndicatorDraftResponse
)

import logging
import os
import re
import json

# LLM 관련 (최신 langchain-openai)
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class ReportService:
    """ESG 매뉴얼 기반 보고서 비즈니스 로직 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.report_repository = ReportRepository(db)

        # sentence_transformers 등 무거운 의존성은 RAG 사용 함수에서만 lazy import 하도록 설계
        self._esg_manual_rag = None

        # LLM을 전역에서 생성하지 않습니다. (지표 목록 등 LLM 불필요 API가 500을 내지 않게)
        # self.llm = ChatOpenAI(...)  # ❌ 금지

        self.doc_root = os.getenv("DOC_ROOT", ".")

    # ──────────────────────────────────────────────────────────────────────────────
    # 내부 유틸: LLM 빌더 (필요한 함수 안에서만 호출)
    # ──────────────────────────────────────────────────────────────────────────────
    def _build_llm(self) -> ChatOpenAI:
        """
        기본 설정으로 ChatOpenAI 초기화.
        OPENAI_API_KEY / OPENAI_MODEL 환경변수 사용.
        """
        try:
            # ✅ 방어: 혹시 남아 있을지 모르는 프록시 ENV 무시 (OpenAI 1.x 'proxies' 인자 미지원 이슈 회피)
            for k in ("OPENAI_PROXY", "HTTP_PROXY", "HTTPS_PROXY",
                      "http_proxy", "https_proxy", "ALL_PROXY"):
                os.environ.pop(k, None)

            return ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                temperature=0.3,
                max_tokens=3000,
                openai_api_key=os.getenv("OPENAI_API_KEY")  # api_key -> openai_api_key
            )
        except Exception as e:
            logger.error(f"ChatOpenAI 초기화 실패: {e}")
            raise

    @property
    def esg_manual_rag(self):
        """RAGUtils lazy loading (임베딩 유틸은 실제 필요 시에만 import)"""
        if self._esg_manual_rag is None:
            from .rag_utils import RAGUtils  # <- lazy import
            self._esg_manual_rag = RAGUtils(collection_name="esg_manual")
        return self._esg_manual_rag

    # ===== CRUD =====
    def create_report(self, request: ReportCreateRequest) -> ReportCreateResponse:
        try:
            existing_report = self.report_repository.get_report(request.topic, request.company_name)
            if existing_report:
                return ReportCreateResponse(
                    success=False, message="이미 존재하는 보고서입니다.",
                    report_id=existing_report.id, topic=request.topic,
                    company_name=request.company_name, report_type=request.report_type
                )

            new_report = self.report_repository.create_report(
                topic=request.topic,
                company_name=request.company_name,
                report_type=request.report_type,
                title=request.title,
                content=request.content,
                metadata=request.metadata
            )

            return ReportCreateResponse(
                success=True, message="보고서가 성공적으로 생성되었습니다.",
                report_id=new_report.id, topic=new_report.topic,
                company_name=new_report.company_name, report_type=new_report.report_type
            )
        except Exception as e:
            logger.exception("보고서 생성 실패")
            return ReportCreateResponse(
                success=False, message=f"보고서 생성 중 오류가 발생했습니다: {str(e)}",
                report_id=0, topic=request.topic,
                company_name=request.company_name, report_type=request.report_type
            )

    def get_report(self, request: ReportGetRequest) -> ReportGetResponse:
        try:
            report = self.report_repository.get_report(request.topic, request.company_name)
            if not report:
                raise ValueError("보고서를 찾을 수 없습니다.")

            return ReportGetResponse(
                success=True, message="보고서를 성공적으로 조회했습니다.",
                id=report.id, topic=report.topic, company_name=report.company_name,
                report_type=report.report_type, title=report.title, content=report.content,
                metadata=getattr(report, "meta", None), status=report.status,
                created_at=report.created_at, updated_at=report.updated_at
            )
        except Exception:
            logger.exception("보고서 조회 실패")
            raise

    def update_report(self, request: ReportUpdateRequest) -> ReportUpdateResponse:
        try:
            updated_report = self.report_repository.update_report(
                topic=request.topic,
                company_name=request.company_name,
                title=request.title,
                content=request.content,
                metadata=request.metadata,
                status=request.status
            )
            if not updated_report:
                return ReportUpdateResponse(success=False, message="업데이트할 보고서를 찾을 수 없습니다.", report_id=0, updated_at=None)

            return ReportUpdateResponse(
                success=True, message="보고서가 성공적으로 업데이트되었습니다.",
                report_id=updated_report.id, updated_at=updated_report.updated_at
            )
        except Exception as e:
            logger.exception("보고서 업데이트 실패")
            return ReportUpdateResponse(
                success=False, message=f"보고서 업데이트 중 오류가 발생했습니다: {str(e)}",
                report_id=0, updated_at=None
            )

    def delete_report(self, request: ReportDeleteRequest) -> ReportDeleteResponse:
        try:
            deleted = self.report_repository.delete_report(request.topic, request.company_name)
            if not deleted:
                return ReportDeleteResponse(success=False, message="삭제할 보고서를 찾을 수 없습니다.", deleted=False)
            return ReportDeleteResponse(success=True, message="보고서가 성공적으로 삭제되었습니다.", deleted=True)
        except Exception as e:
            logger.exception("보고서 삭제 실패")
            return ReportDeleteResponse(success=False, message=f"보고서 삭제 중 오류가 발생했습니다: {str(e)}", deleted=False)

    def get_reports_by_company(self, company_name: str) -> ReportListResponse:
        try:
            reports = self.report_repository.get_reports_by_company(company_name)
            report_responses = [
                ReportGetResponse(
                    success=True, message="",
                    id=r.id, topic=r.topic, company_name=r.company_name,
                    report_type=r.report_type, title=r.title, content=r.content,
                    metadata=getattr(r, "meta", None), status=r.status,
                    created_at=r.created_at, updated_at=r.updated_at
                ) for r in reports
            ]
            return ReportListResponse(
                success=True, message=f"{len(reports)}개의 보고서를 조회했습니다.",
                reports=report_responses, total_count=len(reports)
            )
        except Exception as e:
            logger.exception("회사별 보고서 목록 조회 실패")
            return ReportListResponse(
                success=False, message=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}",
                reports=[], total_count=0
            )

    def get_reports_by_type(self, company_name: str, report_type: str) -> ReportListResponse:
        try:
            reports = self.report_repository.get_reports_by_type(company_name, report_type)
            report_responses = [
                ReportGetResponse(
                    success=True, message="",
                    id=r.id, topic=r.topic, company_name=r.company_name,
                    report_type=r.report_type, title=r.title, content=r.content,
                    metadata=getattr(r, "meta", None), status=r.status,
                    created_at=r.created_at, updated_at=r.updated_at
                ) for r in reports
            ]
            return ReportListResponse(
                success=True, message=f"{len(reports)}개의 {report_type} 보고서를 조회했습니다.",
                reports=report_responses, total_count=len(reports)
            )
        except Exception as e:
            logger.exception("유형별 보고서 목록 조회 실패")
            return ReportListResponse(
                success=False, message=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}",
                reports=[], total_count=0
            )

    def complete_report(self, request: ReportCompleteRequest) -> ReportCompleteResponse:
        try:
            completed = self.report_repository.complete_report(request.topic, request.company_name)
            if not completed:
                return ReportCompleteResponse(success=False, message="완료 처리할 보고서를 찾을 수 없습니다.", completed=False)
            return ReportCompleteResponse(success=True, message="보고서가 성공적으로 완료 처리되었습니다.", completed=True)
        except Exception as e:
            logger.exception("보고서 완료 처리 실패")
            return ReportCompleteResponse(
                success=False, message=f"보고서 완료 처리 중 오류가 발생했습니다: {str(e)}",
                completed=False
            )

    def get_report_status(self, company_name: str) -> Dict[str, str]:
        try:
            return self.report_repository.get_report_status(company_name)
        except Exception as e:
            logger.exception("보고서 상태 조회 실패")
            return {}

    # ===== RAG / Indicator =====
    def search_indicator(self, indicator_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """지표별 ESG 매뉴얼 검색 (KBZ 테이블의 title과 Qdrant 메타데이터 매칭)"""
        try:
            logger.info(f"🔍 RAG 검색 시작: 지표 ID = {indicator_id}")
            
            # 1. KBZ 테이블에서 해당 지표의 실제 title 가져오기
            kbz_indicator = self.report_repository.get_indicator_by_id(indicator_id)
            if not kbz_indicator:
                logger.warning(f"⚠️ KBZ 테이블에서 지표를 찾을 수 없음: {indicator_id}")
                return []
            
            # 2. KBZ 테이블의 title과 subcategory를 검색 쿼리로 사용
            search_title = kbz_indicator.title
            search_subtitle = getattr(kbz_indicator, "subcategory", None)  # sub_title -> subcategory로 수정
            
            logger.info(f"🔍 KBZ 테이블 title로 검색: {search_title}")
            if search_subtitle:
                logger.info(f"🔍 KBZ 테이블 sub_title로도 검색 가능: {search_subtitle}")
            
            # 3. Qdrant에서 title과 sub_title로 검색 (정확한 매칭 + 부분 매칭 시도)
            try:
                # 먼저 정확한 title로 검색
                results = self.esg_manual_rag.search_similar(search_title, limit=limit or 100)
                
                # title로 찾지 못했고 sub_title이 있으면 sub_title로 검색
                if (not results or len(results) == 0) and search_subtitle:
                    logger.info(f"🔍 title 매칭 실패, sub_title로 검색 시도: {search_subtitle}")
                    results = self.esg_manual_rag.search_similar(search_subtitle, limit=limit or 100)
                    if results and len(results) > 0:
                        logger.info(f"✅ sub_title '{search_subtitle}'로 {len(results)}개 결과 발견")
                
                # 여전히 없으면 부분 매칭 시도
                if not results or len(results) == 0:
                    logger.info(f"🔍 정확한 매칭 실패, 부분 매칭 시도: {search_title}")
                    
                    # title에서 키워드 추출 (예: "사업장 안전보건 활동" -> "안전보건")
                    keywords = search_title.split()
                    if len(keywords) > 1:
                        # 가장 중요한 키워드들로 검색
                        important_keywords = [kw for kw in keywords if len(kw) > 1]
                        for keyword in important_keywords[:3]:  # 상위 3개 키워드만 시도
                            logger.info(f"🔍 키워드 검색 시도: {keyword}")
                            keyword_results = self.esg_manual_rag.search_similar(keyword, limit=limit or 50)
                            if keyword_results and len(keyword_results) > 0:
                                results = keyword_results
                                logger.info(f"✅ 키워드 '{keyword}'로 {len(results)}개 결과 발견")
                                break
                
                if isinstance(results, list) and results:
                    logger.info(f"✅ Qdrant에서 총 {len(results)}개 결과 발견")
                    
                    # 중복 제거 (chunk_id 기준) 및 점수 순 정렬
                    seen_chunks = set()
                    unique_results = []
                    for result in results:
                        chunk_id = result.get("chunk_id", "")
                        if chunk_id and chunk_id not in seen_chunks:
                            seen_chunks.add(chunk_id)
                            unique_results.append(result)
                    
                    # 점수 순으로 정렬 (높은 점수 우선)
                    unique_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
                    raw = unique_results
                else:
                    logger.warning(f"⚠️ Qdrant에서 결과를 찾을 수 없음: {search_title}")
                    raw = []
            except Exception as e:
                logger.error(f"❌ Qdrant 검색 실패: {e}")
                raw = []
            
            logger.info(f"📊 RAG 검색 결과: {len(raw) if isinstance(raw, list) else 'error'} 개")
            
            if isinstance(raw, dict) and raw.get("status") == "error":
                logger.error(f"❌ RAG search error: {raw.get('message')}")
                return []

            if isinstance(raw, list):
                logger.info(f"📋 검색된 청크들:")
                for i, r in enumerate(raw):
                    logger.info(f"  {i+1}. Score: {r.get('score', 0.0):.3f}")
                    logger.info(f"     Title: {r.get('title', 'N/A')}")
                    logger.info(f"     Content: {r.get('content', 'N/A')[:100]}...")
                    logger.info(f"     Metadata: {r.get('metadata', {})}")

            processed = []
            for r in raw:
                processed.append({
                    "doc_id": r.get("doc_id", ""),
                    "chunk_id": r.get("chunk_id", ""),
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "pages": r.get("pages", []),
                    "tables": r.get("tables", []),
                    "images": r.get("images", []),
                    "order": r.get("order", 0),
                    "score": r.get("score", 0.0),
                })
            
            logger.info(f"✅ 처리된 결과: {len(processed)} 개")
            return processed
        except Exception as e:
            logger.warning(f"❌ RAG 검색 실패 (지표: {indicator_id}): {e}")
            # RAG 실패 시에도 기본 응답 반환
            return []

    def get_indicator_summary(self, indicator_id: str) -> str:
        try:
            documents = self.search_indicator(indicator_id, limit=3)
            if not documents:
                return "해당 지표에 대한 정보를 찾을 수 없습니다. RAG 검색 결과가 없습니다."

            content = "\n".join([doc.get("content", "") for doc in documents])
            system = SystemMessage(content="""
            너는 ESG 보고서 작성 전문가야.
            아래 지표 설명 텍스트를 바탕으로 다음과 같이 요약해줘:
            - 이 지표의 목적과 의미를 1문장으로 설명하고, *줄을 바꾼 후에* 작성 방법이나 보고 시 유의할 점을 1~2문장으로 요약해줘
            - 화려한 문구 없이 명확하고 실용적으로 써줘
            - 반드시 지표 설명 텍스트의 내용을 기반으로, 지어내지 말고 써줘
            """)
            user = HumanMessage(content=f"[지표 ID: {indicator_id}]\n\n{content}")

            llm = self._build_llm()
            response = llm.invoke([system, user])
            return response.content.strip()
        except Exception:
            logger.exception("지표 요약 생성 실패")
            return "지표 요약 생성 중 오류가 발생했습니다."

    def extract_작성내용(self, chunks: List[str]) -> str:
        """'작성 내용' 블록만 추출"""
        lines = "\n".join(chunks).splitlines()
        capture = False
        result = []
        for line in lines:
            s = line.strip()
            if "작성 내용" in s:
                capture = True
            elif s.startswith("▶") or s.startswith("KBZ-"):
                if capture:
                    break
            if capture:
                result.append(s)
        return "\n".join(result).strip()

    def parse_markdown_to_fields(self, markdown: str) -> List[Dict[str, Any]]:
        """LLM 출력 마크다운 → 입력 필드 구조"""
        rows: List[Dict[str, Any]] = []
        lines = markdown.strip().splitlines()
        current: Dict[str, Any] = {}

        for line in lines:
            line = line.strip()
            m = re.match(r"^\d+\.\s+(?:\*\*)?(.+?)(?:\*\*)?$", line)
            if m:
                if current.get("항목"):
                    rows.append(current)
                current = {"항목": m.group(1).strip()}
                continue
            if "**단위**" in line:
                m = re.search(r"\*\*단위\*\*:\s*(.+)", line)
                if m:
                    current["단위"] = m.group(1).strip()
            elif "**연도별 데이터**" in line:
                m = re.search(r"\*\*연도별 데이터\*\*:\s*(.+)", line)
                if m:
                    current["연도"] = m.group(1).strip()
            elif "**설명**" in line:
                m = re.search(r"\*\*설명\*\*:\s*(.+)", line)
                if m:
                    current["설명"] = m.group(1).strip()

        if current.get("항목"):
            rows.append(current)
        return rows

    def _read_text_files(self, paths: List[str]) -> List[str]:
        """테이블 HTML 파일 경로 목록을 읽어 본문 삽입용 문자열 리스트로 반환"""
        out: List[str] = []
        for p in paths or []:
            abs_path = os.path.join(self.doc_root, p)
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    out.append(f.read())
            except UnicodeDecodeError:
                with open(abs_path, "r", encoding="cp949", errors="ignore") as f:
                    out.append(f.read())
            except Exception as e:
                logger.warning(f"표 파일 로드 실패: {abs_path} ({e})")
        return out

    def generate_input_fields(self, indicator_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"🎯 입력 필드 생성 시작: 지표 ID = {indicator_id}")
            
            documents = self.search_indicator(indicator_id, limit=5)
            logger.info(f"📄 검색된 문서 수: {len(documents)}")
            
            if not documents:
                logger.warning(f"⚠️ 문서를 찾을 수 없음: {indicator_id}")
                return {
                    "indicator_id": indicator_id,
                    "required_data": "",
                    "required_fields": []
                }

            chunks = [d.get("content", "") for d in documents]
            logger.info(f"📝 추출된 청크 수: {len(chunks)}")
            logger.info(f"📄 첫 번째 청크 내용: {chunks[0][:200] if chunks else 'N/A'}...")

            system = SystemMessage(content="""
            너는 ESG 보고서 작성 지원 도우미야.
            사용자가 제공한 지표 설명(청크), 작성 가이드를 바탕으로,
            **이 지표를 작성하기 위해 추가로 입력받아야 할 데이터를** 정리해줘.

            📌 특히 주의할 점:
            - 반드시 **'작성 내용' 항목**을 우선적으로 분석해서, 해당 내용을 보고하기 위해 필요한 입력 항목을 빠짐없이 추출해줘.
            - 작성 내용에 있는 항목은 표에 없어도 반드시 포함해.
            - **표는 참고 자료일 뿐이야. 작성 내용이 중요해.**
            - "건수" 위주의 중복 항목은 제외.

            📋 출력 형식 (엄수)
            1. 필요한 데이터 항목명 (단위 포함 금지)
            2. 단위
            3. 연도 범위 (예: 2021~2023)
            4. 설명
            """)
            작성_블록 = self.extract_작성내용(chunks)
            logger.info(f"📋 추출된 작성 내용: {작성_블록[:200] if 작성_블록 else 'N/A'}...")
            
            user = HumanMessage(content=f"[지표 ID: {indicator_id}]\n\n{chr(10).join(chunks)}\n\n[작성 내용]\n{작성_블록}")

            logger.info(f"🤖 LLM 호출 시작...")
            llm = self._build_llm()
            resp = llm.invoke([system, user])
            logger.info(f"🤖 LLM 응답 완료: {len(resp.content)} 문자")
            
            parsed = self.parse_markdown_to_fields(resp.content)
            logger.info(f"📊 파싱된 필드 수: {len(parsed)}")
            for i, field in enumerate(parsed):
                logger.info(f"  {i+1}. {field.get('항목', 'N/A')}")

            return {"indicator_id": indicator_id, "required_data": resp.content, "required_fields": parsed}
        except Exception as e:
            logger.warning(f"❌ 입력 필드 생성 실패 (지표: {indicator_id}): {e}")
            # RAG/LLM 실패 시에도 기본 응답 반환
            return {
                "indicator_id": indicator_id, 
                "required_data": "", 
                "required_fields": []
            }

    def generate_indicator_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> str:
        try:
            docs = self.search_indicator(indicator_id, limit=5)
            if not docs:
                return "해당 지표에 대한 정보를 찾을 수 없습니다. RAG 검색 결과가 없습니다."

            chunks = [d.get("content", "") for d in docs]
            table_paths: List[str] = []
            for d in docs:
                table_paths.extend(d.get("tables", []) or [])
            table_htmls = self._read_text_files(table_paths)

            system = SystemMessage(content="""
            너는 ESG 보고서를 작성하는 전문 컨설턴트야.
            제공한 지표 설명과 표 HTML을 바탕으로 보고서 초안을 작성해.

            ▶ 전반 톤&스타일
            - 공식적·객관적 문체, 사실/수치 중심, 격식체 종결.
            - 추측/원인 해석/메타표현 금지.

            ▶ 구조
            1) 의미별 소제목 2개 이상 구성
            2) 소제목별로 사용자 입력값을 서술형으로 자연스럽게 녹여 쓰기(단답 나열 금지)
            3) 표 HTML은 **본문에 그대로 삽입**하고, 각 표는 한 줄 설명 뒤에 `<table>...</table>` 원문을 그대로 넣기
               (여러 표가 있어도 모두 삽입. 요약/생략 절대 금지)

            ▶ 수치/표 규칙
            - 표의 수치를 본문에 반복해서 쓰지 말 것(표로만 제시).
            """)
            flat_inputs: List[str] = []
            for k, v in inputs.items():
                if isinstance(v, dict):
                    for sk, sv in v.items():
                        flat_inputs.append(f"- {k} ({sk}): {sv}")
                else:
                    flat_inputs.append(f"- {k}: {v}")

            user = HumanMessage(content=f"""
            [지표 ID] {indicator_id}
            [회사명] {company_name}

            [지표 설명 텍스트]
            {chr(10).join(chunks)}

            [표 HTML 원문들]
            {chr(10).join(table_htmls)}

            [사용자 입력 데이터]
            {chr(10).join(flat_inputs)}
            """)

            llm = self._build_llm()
            resp = llm.invoke([system, user])
            return resp.content.strip()
        except Exception:
            logger.exception("초안 생성 실패")
            return "⚠️ 초안 생성 중 오류가 발생했습니다."

    def save_indicator_data(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> bool:
        try:
            existing = self.report_repository.get_report(indicator_id, company_name)
            if existing:
                self.report_repository.update_report(
                    topic=indicator_id, company_name=company_name, metadata={"inputs": inputs}
                )
            else:
                self.report_repository.create_report(
                    topic=indicator_id, company_name=company_name, report_type="indicator",
                    title=f"{indicator_id} 보고서", content="", metadata={"inputs": inputs}
                )
            return True
        except Exception:
            logger.exception("지표 데이터 저장 실패")
            return False

    def get_indicator_data(self, indicator_id: str, company_name: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.report_repository.get_report(indicator_id, company_name)
            if r and getattr(r, "meta", None):
                return r.meta.get("inputs", {})
            return None
        except Exception:
            logger.exception("지표 데이터 조회 실패")
            return None

    # ===== 지표 관리 =====
    def get_all_indicators(self) -> IndicatorListResponse:
        try:
            indicators = self.report_repository.get_all_indicators()
            indicator_responses = []
            for indicator in indicators:
                indicator_responses.append(IndicatorResponse(
                    success=True,
                    message="",
                    indicator_id=indicator.indicator_id,
                    title=indicator.title,
                    category=indicator.category,
                    subcategory=indicator.subcategory,
                    description=indicator.description,
                    input_fields=indicator.input_fields,
                    example_data=indicator.example_data,
                    status=indicator.status,
                    created_at=indicator.created_at,
                    updated_at=indicator.updated_at
                ))
            return IndicatorListResponse(
                success=True,
                message=f"{len(indicator_responses)}개의 지표를 조회했습니다.",
                indicators=indicator_responses,
                total_count=len(indicator_responses)
            )
        except Exception as e:
            logger.exception("지표 목록 조회 실패")
            return IndicatorListResponse(
                success=False,
                message=f"지표 목록 조회 중 오류가 발생했습니다: {str(e)}",
                indicators=[],
                total_count=0
            )

    def get_indicators_by_category(self, category: str) -> IndicatorListResponse:
        try:
            indicators = self.report_repository.get_indicators_by_category(category)
            indicator_responses = []
            for indicator in indicators:
                indicator_responses.append(IndicatorResponse(
                    success=True,
                    message="",
                    indicator_id=indicator.indicator_id,
                    title=indicator.title,
                    category=indicator.category,
                    subcategory=indicator.subcategory,
                    description=indicator.description,
                    input_fields=indicator.input_fields,
                    example_data=indicator.example_data,
                    status=indicator.status,
                    created_at=indicator.created_at,
                    updated_at=indicator.updated_at
                ))
            return IndicatorListResponse(
                success=True,
                message=f"{category} 카테고리의 {len(indicator_responses)}개 지표를 조회했습니다.",
                indicators=indicator_responses,
                total_count=len(indicator_responses)
            )
        except Exception as e:
            logger.exception(f"{category} 카테고리 지표 조회 실패")
            return IndicatorListResponse(
                success=False,
                message=f"{category} 카테고리 지표 조회 중 오류가 발생했습니다: {str(e)}",
                indicators=[],
                total_count=0
            )

    # ===== 개별 지표 처리 메서드 (새로 추가) =====
    def process_single_indicator(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> IndicatorDraftResponse:
        """
        개별 지표 처리: 입력필드 생성 → 초안 생성 (한 번에 처리)
        """
        try:
            # 1. 지표 정보 조회
            indicator = self.report_repository.get_indicator_by_id(indicator_id)
            if not indicator:
                return IndicatorDraftResponse(
                    success=False,
                    message=f"지표 {indicator_id}를 찾을 수 없습니다.",
                    indicator_id=indicator_id,
                    company_name=company_name,
                    draft_content="",
                    generated_at=datetime.now()
                )

            # 2. RAG 기반 입력필드 생성 (필요시)
            if not inputs:
                inputs = self.generate_input_fields_only(indicator_id)
            
            # 3. 필드 스키마를 값으로 변환 (보정)
            inputs = self._coerce_field_schema_to_values(inputs)

            # 4. 초안 생성
            draft_content = self.generate_indicator_draft(indicator_id, company_name, inputs)

            return IndicatorDraftResponse(
                success=True,
                message="개별 지표 처리가 성공적으로 완료되었습니다.",
                indicator_id=indicator_id,
                company_name=company_name,
                draft_content=draft_content,
                generated_at=datetime.now()
            )
        except Exception as e:
            logger.exception(f"개별 지표 처리 실패: {indicator_id}")
            return IndicatorDraftResponse(
                success=False,
                message=f"개별 지표 처리 중 오류가 발생했습니다: {str(e)}",
                indicator_id=indicator_id,
                company_name=company_name,
                draft_content="",
                generated_at=datetime.now()
            )

    def generate_input_fields_only(self, indicator_id: str) -> Dict[str, Any]:
        """
        개별 지표의 입력필드만 생성 (RAG 기반 AI 생성)
        """
        try:
            indicator = self.report_repository.get_indicator_by_id(indicator_id)
            if not indicator:
                logger.warning(f"⚠️ 지표를 찾을 수 없음: {indicator_id}")
                return {}

            # search_indicator 메서드를 사용하여 KBZ 테이블의 title로 정확한 검색
            search_results = self.search_indicator(indicator_id, limit=10)  # 더 많은 결과 검색
            logger.info(f"📄 검색된 문서 수: {len(search_results)}")

            if not search_results:
                logger.warning(f"⚠️ 문서를 찾을 수 없음: {indicator_id}")
                return {}

            # RAG 검색 결과를 기반으로 AI가 입력필드 생성
            chunks = [result.get("content", "") for result in search_results]
            작성_블록 = self.extract_작성내용(chunks)
            
            system = SystemMessage(content="""
너는 ESG 보고서 작성 지원 도우미야.
사용자가 제공한 지표 설명과 작성 가이드를 바탕으로,
이 지표를 작성하기 위해 추가로 입력받아야 할 데이터를 JSON 형태로 정리해줘.

📌 분석 기준:
1. **작성 내용**을 우선적으로 분석해서 필요한 입력 항목을 추출
2. 작성 내용에 있는 항목은 표에 없어도 반드시 포함
3. "건수" 위주의 중복 항목은 제외
4. 실제로 수집 가능한 데이터인지 확인

📋 출력 형식 (엄수):
{
    "field_name": {
        "type": "number|text|select|textarea",
        "label": "한글 라벨",
        "description": "상세 설명",
        "required": true|false,
        "unit": "단위 (선택사항)",
        "options": ["옵션1", "옵션2"] (select 타입인 경우),
        "placeholder": "입력 예시 (선택사항)"
    }
}

⚠️ 중요: 반드시 유효한 JSON 형식으로만 응답해줘. 다른 텍스트는 포함하지 마.
""")
            
            user = HumanMessage(content=f"""
[지표 ID: {indicator_id}]

지표 설명:
{chr(10).join(chunks)}

작성 내용:
{작성_블록}

위 정보를 바탕으로 이 지표 작성에 필요한 입력필드를 JSON 형태로 생성해줘.
""")

            logger.info(f"🤖 AI 입력필드 생성 시작...")
            llm = self._build_llm()
            resp = llm.invoke([system, user])
            logger.info(f"🤖 AI 입력필드 생성 완료: {len(resp.content)} 문자")
            
            # JSON 파싱 (더 안전한 방식)
            try:
                import json
                import re
                
                # JSON 부분만 추출
                content = resp.content.strip()
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    input_fields = json.loads(json_str)
                else:
                    # 전체 내용을 JSON으로 파싱 시도
                    input_fields = json.loads(content)
                
                logger.info(f"📊 생성된 입력필드 수: {len(input_fields)}")
                for field_name, field_config in input_fields.items():
                    logger.info(f"  - {field_name}: {field_config.get('label', 'N/A')}")
                
                return input_fields
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON 파싱 실패: {e}")
                logger.error(f"응답 내용: {resp.content}")
                
                # 파싱 실패 시 기본 필드 반환
                return {
                    "company_name": {
                        "type": "text",
                        "label": "회사명",
                        "description": "보고서 작성 대상 회사명",
                        "required": True
                    },
                    "report_year": {
                        "type": "text",
                        "label": "보고 연도",
                        "description": "보고서 작성 연도",
                        "required": True,
                        "placeholder": "예: 2023"
                    }
                }

        except Exception as e:
            logger.exception(f"입력필드 생성 실패: {indicator_id}")
            return {}

    def generate_indicator_draft_only(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> IndicatorDraftResponse:
        """
        개별 지표의 초안만 생성 (입력된 데이터 기반)
        """
        try:
            indicator = self.report_repository.get_indicator_by_id(indicator_id)
            if not indicator:
                return IndicatorDraftResponse(
                    success=False,
                    message=f"지표 {indicator_id}를 찾을 수 없습니다.",
                    indicator_id=indicator_id,
                    company_name=company_name,
                    draft_content="",
                    generated_at=datetime.now()
                )

            # 초안 생성
            draft_content = self.generate_indicator_draft(indicator_id, company_name, inputs)

            return IndicatorDraftResponse(
                success=True,
                message="지표 초안이 성공적으로 생성되었습니다.",
                indicator_id=indicator_id,
                company_name=company_name,
                draft_content=draft_content,
                generated_at=datetime.now()
            )
        except Exception as e:
            logger.exception(f"지표 초안 생성 실패: {indicator_id}")
            return IndicatorDraftResponse(
                success=False,
                message=f"지표 초안 생성 중 오류가 발생했습니다: {str(e)}",
                indicator_id=indicator_id,
                company_name=company_name,
                draft_content="",
                generated_at=datetime.now()
            )

    def get_indicator_with_recommended_fields(self, indicator_id: str) -> IndicatorInputFieldResponse:
        """
        지표와 함께 추천 필드를 반환
        """
        try:
            indicator = self.report_repository.get_indicator_by_id(indicator_id)
            if not indicator:
                return IndicatorInputFieldResponse(
                    success=False, 
                    message=f"지표 {indicator_id}를 찾을 수 없습니다.",
                    indicator_id=indicator_id, 
                    title="", 
                    input_fields={}, 
                    recommended_fields=[]
                )
            
            # 추천 필드 생성 (기존 generate_input_fields 활용)
            gen = self.generate_input_fields(indicator_id)
            return IndicatorInputFieldResponse(
                success=True, 
                message="입력필드 추천을 생성했습니다.",
                indicator_id=indicator_id,
                title=indicator.title,
                input_fields={},  # 저장된 정의가 있다면 채워넣기
                recommended_fields=gen.get("required_fields", []),
            )
        except Exception as e:
            logger.exception(f"추천 필드 생성 실패: {indicator_id}")
            return IndicatorInputFieldResponse(
                success=False,
                message=f"추천 필드 생성 중 오류가 발생했습니다: {str(e)}",
                indicator_id=indicator_id,
                title="",
                input_fields={},
                recommended_fields=[]
            )

    def generate_enhanced_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> IndicatorDraftResponse:
        """
        향상된 초안 생성
        """
        try:
            draft = self.generate_indicator_draft(indicator_id, company_name, inputs)
            return IndicatorDraftResponse(
                success=True, 
                message="향상된 초안을 생성했습니다.",
                indicator_id=indicator_id, 
                company_name=company_name,
                draft_content=draft, 
                generated_at=datetime.now()
            )
        except Exception as e:
            logger.exception(f"향상된 초안 생성 실패: {indicator_id}")
            return IndicatorDraftResponse(
                success=False,
                message=f"향상된 초안 생성 중 오류가 발생했습니다: {str(e)}",
                indicator_id=indicator_id,
                company_name=company_name,
                draft_content="",
                generated_at=datetime.now()
            )

    def _coerce_field_schema_to_values(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        필드 스키마를 값으로 변환
        {"field": {"type": "...", "label": "...", ...}} -> {"field": ""}
        """
        if not inputs: 
            return {}
        out = {}
        for k, v in inputs.items():
            out[k] = "" if isinstance(v, dict) else v
        return out
