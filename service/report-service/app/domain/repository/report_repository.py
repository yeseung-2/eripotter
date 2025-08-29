"""
Report Repository - Report 엔터티 CRUD/조회
- Entity의 예약어 충돌을 피하기 위해, 파이썬 속성명은 meta(컬럼명은 "metadata")
- (topic, company_name) 유니크 제약 기반의 안전한 생성/업데이트
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..entity.report_entity import Report, Indicator


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- helpers ----------
    def _get_by_topic_company(self, topic: str, company_name: str) -> Optional[Report]:
        stmt = select(Report).where(
            and_(Report.topic == topic, Report.company_name == company_name)
        )
        return self.db.scalar(stmt)

    # ---------- CRUD ----------
    def get_report(self, topic: str, company_name: str) -> Optional[Report]:
        """단일 보고서 조회"""
        return self._get_by_topic_company(topic, company_name)

    def create_report(
        self,
        *,
        topic: str,
        company_name: str,
        report_type: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "draft",
    ) -> Report:
        """
        보고서 생성
        - meta 컬럼에 metadata 매핑
        - (topic, company_name) 유니크 충돌 시 기존 레코드 반환 (멱등성)
        """
        obj = Report(
            topic=topic,
            company_name=company_name,
            report_type=report_type,
            title=title,
            content=content,
            meta=metadata,          # <-- 속성명은 meta
            status=status,
        )
        self.db.add(obj)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            # 이미 존재하면 기존 객체 반환 (서비스 레이어에서 메시지 제어)
            existing = self._get_by_topic_company(topic, company_name)
            if existing:
                return existing
            # 혹시라도 없으면 재-예외
            raise
        self.db.refresh(obj)
        return obj

    def update_report(
        self,
        *,
        topic: str,
        company_name: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Optional[Report]:
        """
        부분 업데이트
        - 전달된 필드만 변경
        - metadata는 통째 교체(머지 원하면 여기서 merge 로직 추가)
        """
        obj = self._get_by_topic_company(topic, company_name)
        if not obj:
            return None

        if title is not None:
            obj.title = title
        if content is not None:
            obj.content = content
        if metadata is not None:
            obj.meta = metadata      # <-- 속성명은 meta
        if status is not None:
            obj.status = status

        # updated_at은 모델에서 server_default+onupdate 이지만,
        # 일부 DB 드라이버/버전 환경에서 즉시 반영 안 될 수 있어 수동 터치 보완
        try:
            # 수동 터치(선택): obj.updated_at = datetime.utcnow()
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(obj)
        return obj

    def delete_report(self, topic: str, company_name: str) -> bool:
        obj = self._get_by_topic_company(topic, company_name)
        if not obj:
            return False
        self.db.delete(obj)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return True

    # ---------- lists / status ----------
    def get_reports_by_company(self, company_name: str) -> List[Report]:
        stmt = select(Report).where(Report.company_name == company_name).order_by(Report.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_reports_by_type(self, company_name: str, report_type: str) -> List[Report]:
        stmt = (
            select(Report)
            .where(and_(Report.company_name == company_name, Report.report_type == report_type))
            .order_by(Report.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def complete_report(self, topic: str, company_name: str) -> bool:
        obj = self._get_by_topic_company(topic, company_name)
        if not obj:
            return False
        obj.status = "completed"
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return True

    def get_report_status(self, company_name: str) -> Dict[str, str]:
        """
        회사별 (topic -> status) 맵 반환
        - 프런트에서 진행 현황 표시 등에 사용
        """
        stmt = select(Report.topic, Report.status).where(Report.company_name == company_name)
        rows = self.db.execute(stmt).all()
        return {topic: status for (topic, status) in rows}

    # ===== Indicator Repository Methods =====
    
    def get_all_indicators(self) -> List[Indicator]:
        """모든 활성 지표 조회"""
        stmt = select(Indicator).where(Indicator.status == "active").order_by(Indicator.category, Indicator.indicator_id)
        return list(self.db.scalars(stmt).all())
    
    def get_indicators_by_category(self, category: str) -> List[Indicator]:
        """카테고리별 지표 조회"""
        stmt = select(Indicator).where(
            and_(Indicator.category == category, Indicator.status == "active")
        ).order_by(Indicator.indicator_id)
        return list(self.db.scalars(stmt).all())
    
    def get_indicator_by_id(self, indicator_id: str) -> Optional[Indicator]:
        """지표 ID로 지표 조회"""
        stmt = select(Indicator).where(Indicator.indicator_id == indicator_id)
        return self.db.scalar(stmt)
    
    def create_indicator(
        self,
        *,
        indicator_id: str,
        title: str,
        category: str,
        subcategory: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[Dict[str, Any]] = None,
        example_data: Optional[Dict[str, Any]] = None,
        status: str = "active",
    ) -> Indicator:
        """지표 생성"""
        obj = Indicator(
            indicator_id=indicator_id,
            title=title,
            category=category,
            subcategory=subcategory,
            description=description,
            input_fields=input_fields,
            example_data=example_data,
            status=status,
        )
        self.db.add(obj)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            # 이미 존재하면 기존 객체 반환
            existing = self.get_indicator_by_id(indicator_id)
            if existing:
                return existing
            raise
        self.db.refresh(obj)
        return obj
    
    def update_indicator(
        self,
        *,
        indicator_id: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[Dict[str, Any]] = None,
        example_data: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Optional[Indicator]:
        """지표 업데이트"""
        obj = self.get_indicator_by_id(indicator_id)
        if not obj:
            return None
            
        if title is not None:
            obj.title = title
        if category is not None:
            obj.category = category
        if subcategory is not None:
            obj.subcategory = subcategory
        if description is not None:
            obj.description = description
        if input_fields is not None:
            obj.input_fields = input_fields
        if example_data is not None:
            obj.example_data = example_data
        if status is not None:
            obj.status = status
            
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(obj)
        return obj
