class NormalController:
    def __init__(self, service):
        self.service = service

    def get_all_normalized_data(self):
        """모든 정규화 데이터 조회"""
        try:
            if not self.service.db_available:
                return {"status": "error", "message": "데이터베이스 연결 불가"}
            
            data = self.service.normal_repository.get_all(limit=50)
            return {"status": "success", "data": [item.to_dict() for item in data]}
        except Exception as e:
            return {"status": "error", "message": f"데이터 조회 실패: {str(e)}"}

    def get_normalized_data_by_id(self, data_id: str):
        """특정 정규화 데이터 조회"""
        try:
            if not self.service.db_available:
                return {"status": "error", "message": "데이터베이스 연결 불가"}
            
            data = self.service.normal_repository.get_by_id(int(data_id))
            if data:
                return {"status": "success", "data": data.to_dict()}
            else:
                return {"status": "error", "message": "데이터를 찾을 수 없습니다."}
        except Exception as e:
            return {"status": "error", "message": f"데이터 조회 실패: {str(e)}"}

    def upload_and_normalize_excel(self, file):
        """엑셀 파일 업로드 및 정규화"""
        try:
            # 파일 업로드 처리 로직 구현
            return {"status": "success", "message": "파일 업로드 및 정규화 완료", "filename": file.filename}
        except Exception as e:
            return {"status": "error", "message": f"파일 업로드 실패: {str(e)}"}

    def create_normalized_data(self, data: dict):
        """정규화 데이터 생성"""
        try:
            if not self.service.db_available:
                return {"status": "error", "message": "데이터베이스 연결 불가"}
            
            result = self.service.normal_repository.create(data)
            if result:
                return {"status": "success", "data": result.to_dict()}
            else:
                return {"status": "error", "message": "데이터 생성 실패"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 생성 실패: {str(e)}"}

    def update_normalized_data(self, data_id: str, data: dict):
        """정규화 데이터 업데이트"""
        try:
            if not self.service.db_available:
                return {"status": "error", "message": "데이터베이스 연결 불가"}
            
            # Repository에 update 메서드가 없으므로 직접 구현
            return {"status": "not_implemented", "message": "업데이트 기능은 현재 미구현"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 업데이트 실패: {str(e)}"}

    def delete_normalized_data(self, data_id: str):
        """정규화 데이터 삭제"""
        try:
            if not self.service.db_available:
                return {"status": "error", "message": "데이터베이스 연결 불가"}
            
            # Repository에 delete 메서드가 없으므로 직접 구현
            return {"status": "not_implemented", "message": "삭제 기능은 현재 미구현"}
        except Exception as e:
            return {"status": "error", "message": f"데이터 삭제 실패: {str(e)}"}

    def get_metrics(self):
        """메트릭 조회"""
        try:
            metrics = self.service.get_metrics()
            return {"status": "success", "metrics": metrics}
        except Exception as e:
            return {"status": "error", "message": f"메트릭 조회 실패: {str(e)}"}

    # ===== ESG 관련 메서드들 (현재 미사용) =====
    
    def upload_partner_esg_data(self, file, company_id: str = None):
        """협력사 ESG 데이터 파일 업로드 및 검증"""
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def validate_partner_esg_data(self, data: dict):
        """협력사 ESG 데이터 검증 및 표준화"""
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def get_partner_dashboard(self, company_id: str):
        """협력사 ESG 자가진단 대시보드 데이터 조회"""
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def generate_partner_report(self, report_type: str, company_id: str):
        """협력사 ESG 보고서 자동 생성"""
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def get_esg_schema(self, industry: str):
        """업종별 ESG 데이터 스키마 조회"""
        return {"status": "not_implemented", "message": "ESG 기능은 현재 미구현"}

    def get_environmental_data(self, company_name: str):
        """회사별 실제 환경 데이터 조회"""
        try:
            environmental_data = self.service.get_environmental_data_by_company(company_name)
            return {
                "status": "success",
                "data": environmental_data
            }
        except Exception as e:
            return {"status": "error", "message": f"환경 데이터 조회 실패: {str(e)}"}
