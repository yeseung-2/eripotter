"""
Report Service - ESG 매뉴얼 기반 보고서 비즈니스 로직 처리
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..repository.report_repository import ReportRepository
from ..model.report_model import (
    ReportCreateRequest, ReportCreateResponse,
    ReportGetRequest, ReportGetResponse,
    ReportUpdateRequest, ReportUpdateResponse,
    ReportDeleteRequest, ReportDeleteResponse,
    ReportListResponse, ReportCompleteRequest, ReportCompleteResponse
)
from .rag_utils import RAGUtils
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import logging
import os
import re

logger = logging.getLogger(__name__)

class ReportService:
    """ESG 매뉴얼 기반 보고서 비즈니스 로직 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.report_repository = ReportRepository(db)
        self.esg_manual_rag = RAGUtils(collection_name="esg_manual")
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.3,
            max_tokens=3000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.doc_root = os.getenv("DOC_ROOT", ".")  # 표/이미지 등 로컬 리소스 루트

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
                # Entity 속성은 meta지만, 레포지토리에서 올바르게 매핑해야 함
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
                return ReportGetResponse(
                    success=False, message="보고서를 찾을 수 없습니다.",
                    id=0, topic=request.topic, company_name=request.company_name,
                    report_type="", title=None, content=None, metadata=None,
                    status="", created_at=None, updated_at=None
                )

            return ReportGetResponse(
                success=True, message="보고서를 성공적으로 조회했습니다.",
                id=report.id, topic=report.topic, company_name=report.company_name,
                report_type=report.report_type, title=report.title, content=report.content,
                metadata=getattr(report, "meta", None), status=report.status,
                created_at=report.created_at, updated_at=report.updated_at
            )
        except Exception as e:
            logger.exception("보고서 조회 실패")
            return ReportGetResponse(
                success=False, message=f"보고서 조회 중 오류가 발생했습니다: {str(e)}",
                id=0, topic=request.topic, company_name=request.company_name,
                report_type="", title=None, content=None, metadata=None,
                status="", created_at=None, updated_at=None
            )

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

            return ReportUpdateResponse(success=True, message="보고서가 성공적으로 업데이트되었습니다.",
                                        report_id=updated_report.id, updated_at=updated_report.updated_at)
        except Exception as e:
            logger.exception("보고서 업데이트 실패")
            return ReportUpdateResponse(success=False, message=f"보고서 업데이트 중 오류가 발생했습니다: {str(e)}",
                                        report_id=0, updated_at=None)

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
            return ReportListResponse(success=True, message=f"{len(reports)}개의 보고서를 조회했습니다.",
                                      reports=report_responses, total_count=len(reports))
        except Exception as e:
            logger.exception("회사별 보고서 목록 조회 실패")
            return ReportListResponse(success=False, message=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}",
                                      reports=[], total_count=0)

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
            return ReportListResponse(success=True, message=f"{len(reports)}개의 {report_type} 보고서를 조회했습니다.",
                                      reports=report_responses, total_count=len(reports))
        except Exception as e:
            logger.exception("유형별 보고서 목록 조회 실패")
            return ReportListResponse(success=False, message=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}",
                                      reports=[], total_count=0)

    def complete_report(self, request: ReportCompleteRequest) -> ReportCompleteResponse:
        try:
            completed = self.report_repository.complete_report(request.topic, request.company_name)
            if not completed:
                return ReportCompleteResponse(success=False, message="완료 처리할 보고서를 찾을 수 없습니다.", completed=False)
            return ReportCompleteResponse(success=True, message="보고서가 성공적으로 완료 처리되었습니다.", completed=True)
        except Exception as e:
            logger.exception("보고서 완료 처리 실패")
            return ReportCompleteResponse(success=False, message=f"보고서 완료 처리 중 오류가 발생했습니다: {str(e)}", completed=False)

    def get_report_status(self, company_name: str) -> Dict[str, str]:
        try:
            return self.report_repository.get_report_status(company_name)
        except Exception as e:
            logger.exception("보고서 상태 조회 실패")
            return {}

    # ===== RAG / Indicator =====
    def search_indicator(self, indicator_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        지표별 ESG 매뉴얼 검색.
        - 기본: indicator_id로 의미 검색
        - 결과 필드 표준화
        """
        try:
            raw = self.esg_manual_rag.search_similar(indicator_id, limit=limit)
            if isinstance(raw, dict) and raw.get("status") == "error":
                logger.error(f"RAG search error: {raw.get('message')}")
                return []

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
                    "order": r.get("order", 0)
                })
            return processed
        except Exception as e:
            logger.exception("지표 검색 실패")
            return []

    def get_indicator_summary(self, indicator_id: str) -> str:
        try:
            documents = self.search_indicator(indicator_id, limit=3)
            if not documents:
                return "해당 지표에 대한 정보를 찾을 수 없습니다."

            content = "\n".join([doc.get("content", "") for doc in documents])
            system = SystemMessage(content="""
            너는 ESG 보고서 작성 전문가야.
            아래 지표 설명 텍스트를 바탕으로 다음과 같이 요약해줘:
            - 이 지표의 목적과 의미를 1문장으로 설명하고, *줄을 바꾼 후에* 작성 방법이나 보고 시 유의할 점을 1~2문장으로 요약해줘
            - 화려한 문구 없이 명확하고 실용적으로 써줘
            - 반드시 지표 설명 텍스트의 내용을 기반으로, 지어내지 말고 써줘
            """)
            user = HumanMessage(content=f"[지표 ID: {indicator_id}]\n\n{content}")
            response = self.llm.invoke([system, user])
            return response.content.strip()
        except Exception as e:
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
            # 항목명
            m = re.match(r"^\d+\.\s+(?:\*\*)?(.+?)(?:\*\*)?$", line)
            if m:
                if current.get("항목"):
                    rows.append(current)
                current = {"항목": m.group(1).strip()}
                continue
            # 단위
            if "**단위**" in line:
                m = re.search(r"\*\*단위\*\*:\s*(.+)", line)
                if m:
                    current["단위"] = m.group(1).strip()
            # 연도
            elif "**연도별 데이터**" in line:
                m = re.search(r"\*\*연도별 데이터\*\*:\s*(.+)", line)
                if m:
                    current["연도"] = m.group(1).strip()
            # 설명
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
            documents = self.search_indicator(indicator_id, limit=5)
            if not documents:
                return {"indicator_id": indicator_id, "required_data": "해당 지표에 대한 정보를 찾을 수 없습니다.", "required_fields": []}

            chunks = [d.get("content", "") for d in documents]

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
            user = HumanMessage(content=f"[지표 ID: {indicator_id}]\n\n{'\n'.join(chunks)}\n\n[작성 내용]\n{작성_블록}")
            resp = self.llm.invoke([system, user])
            parsed = self.parse_markdown_to_fields(resp.content)

            return {"indicator_id": indicator_id, "required_data": resp.content, "required_fields": parsed}
        except Exception as e:
            logger.exception("입력 필드 생성 실패")
            return {"indicator_id": indicator_id, "required_data": "⚠️ LLM 호출 중 오류가 발생했습니다.", "required_fields": []}

    def generate_indicator_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> str:
        try:
            docs = self.search_indicator(indicator_id, limit=5)
            if not docs:
                return "해당 지표에 대한 정보를 찾을 수 없습니다."

            chunks = [d.get("content", "") for d in docs]
            # 표 HTML 읽기 (절대 요약/생략 금지)
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

            # 입력값 문자열화
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

            resp = self.llm.invoke([system, user])
            return resp.content.strip()
        except Exception as e:
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
        except Exception as e:
            logger.exception("지표 데이터 저장 실패")
            return False

    def get_indicator_data(self, indicator_id: str, company_name: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.report_repository.get_report(indicator_id, company_name)
            if r and getattr(r, "meta", None):
                return r.meta.get("inputs", {})
            return None
        except Exception as e:
            logger.exception("지표 데이터 조회 실패")
            return None
    
