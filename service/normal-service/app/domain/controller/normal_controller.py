# app/domain/controller/normal_controller.py
"""
Normal Controller (Refactored)
- DB 가용성 체크 및 예외 처리 강화
- update / delete 실구현 (Repository 연결)
- upload_and_normalize_excel: 서비스 구현 존재 시 위임, 없으면 not_implemented
- 응답 포맷 일관성 유지
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class NormalController:
    def __init__(self, service):
        self.service = service

    # ===== Utility =====

    def _ensure_db(self) -> Optional[Dict[str, Any]]:
        """DB 연결 가용성 검사"""
        if not getattr(self.service, "db_available", False):
            return {"status": "error", "message": "데이터베이스 연결 불가"}
        return None

    def _to_int_id(self, data_id: str) -> Optional[int]:
        try:
            return int(data_id)
        except Exception:
            return None

    # ===== Reads =====

    def get_all_normalized_data(self) -> Dict[str, Any]:
        """모든 정규화 데이터 조회"""
        try:
            err = self._ensure_db()
            if err:
                return err

            data = self.service.normal_repository.get_all(limit=50)
            return {"status": "success", "data": [item.to_dict() for item in data]}
        except Exception as e:
            return {"status": "error", "message": f"데이터 조회 실패: {str(e)}"}

    def get_normalized_data_by_id(self, data_id: str) -> Dict[str, Any]:
        """특정 정규화 데이터 조회"""
        try:
            err = self._ensure_db()
            if err:
                return err

            nid = self._to_int_id(data_id)
            if nid is None:
                return {"status": "error", "message": "유효하지 않은 ID 형식입니다."}

            data = self.service.normal_repository.get_by_id(nid)
            if data:
                return {"status": "success", "data": data.to_dict()}
            else:
                return {"status": "error", "message": "데이터를 찾을 수 없습니다."}
        except Exception as e:
            return {"status": "error", "message": f"데이터 조회 실패: {str(e)}"}

    # ===== Create / Update / Delete =====

    def upload_and_normalize_excel(self, file) -> Dict[str, Any]:
        """엑셀 파일 업로드 및 정규화"""
        try:
            # 서비스에 구현되어 있으면 위임 (미구현이면 안전 처리)
            if hasattr(self.service, "upload_and_normalize_excel"):
                return self.service.upload_and_normalize_excel(file)
            return {
                "status": "not_implemented",
                "message": "엑셀 업로드/정규화 기능은 현재 미구현",
                "filename": getattr(file, "filename", None),
            }
        except Exception as e:
            return {"status": "error", "message": f"파일 업로드 실패: {str(e)}"}

    def create_normalized_data(self, data: dict) -> Dict[str, Any]:
        """정규화 데이터 생성"""
        try:
            err = self._ensure_db()
            if err:
                return err

            result = self.service.normal_repository.create(data)
            if result:
                return {"status": "success", "data": result.to_dict()}
            else:
                return {"status": "error", "message": "데이터 생성 실패"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 생성 실패: {str(e)}"}

    def update_normalized_data(self, data_id: str, data: dict) -> Dict[str, Any]:
        """정규화 데이터 업데이트"""
        try:
            err = self._ensure_db()
            if err:
                return err

            nid = self._to_int_id(data_id)
            if nid is None:
                return {"status": "error", "message": "유효하지 않은 ID 형식입니다."}

            ok = self.service.normal_repository.update(nid, data or {})
            if ok:
                # 갱신된 결과도 함께 반환
                updated = self.service.normal_repository.get_by_id(nid)
                return {
                    "status": "success",
                    "message": "업데이트 완료",
                    "data": updated.to_dict() if updated else {"id": nid},
                }
            return {"status": "error", "message": "데이터 업데이트 실패"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 업데이트 실패: {str(e)}"}

    def delete_normalized_data(self, data_id: str) -> Dict[str, Any]:
        """정규화 데이터 삭제"""
        try:
            err = self._ensure_db()
            if err:
                return err

            nid = self._to_int_id(data_id)
            if nid is None:
                return {"status": "error", "message": "유효하지 않은 ID 형식입니다."}

            ok = self.service.normal_repository.delete(nid)
            if ok:
                return {"status": "success", "message": "삭제 완료", "data": {"id": nid}}
            return {"status": "error", "message": "데이터 삭제 실패"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 삭제 실패: {str(e)}"}

    # ===== Metrics =====

    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        try:
            metrics = self.service.get_metrics()
            return {"status": "success", "metrics": metrics}
        except Exception as e:
            return {"status": "error", "message": f"메트릭 조회 실패: {str(e)}"}

    # ===== ESG (현재 미사용) =====

    def upload_partner_esg_data(self, file, company_id: str = None) -> Dict[str, Any]:
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def validate_partner_esg_data(self, data: dict) -> Dict[str, Any]:
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def get_partner_dashboard(self, company_id: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def generate_partner_report(self, report_type: str, company_id: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def get_esg_schema(self, industry: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    # ===== Environmental =====

    def get_environmental_data(self, company_name: str) -> Dict[str, Any]:
        """회사별 실제 환경 데이터 조회"""
        try:
            environmental_data = self.service.get_environmental_data_by_company(company_name)
            return {"status": "success", "data": environmental_data}
        except Exception as e:
            return {"status": "error", "message": f"환경 데이터 조회 실패: {str(e)}"}
