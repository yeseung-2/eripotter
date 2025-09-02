from datetime import datetime

class NormalController:
    def __init__(self, service):
        self.service = service

    def get_all_normalized_data(self):
        """모든 정규화 데이터 조회"""
        return {"status": "success", "data": []}

    def get_normalized_data_by_id(self, data_id: str):
        """특정 정규화 데이터 조회"""
        return {"status": "success", "data": {"id": data_id}}

    def upload_and_normalize_excel(self, file):
        """엑셀 파일 업로드 및 정규화"""
        return {"status": "success", "message": "파일 업로드 및 정규화 완료", "filename": file.filename}

    def create_normalized_data(self, data: dict):
        """정규화 데이터 생성"""
        return {"status": "success", "data": data}

    def update_normalized_data(self, data_id: str, data: dict):
        """정규화 데이터 업데이트"""
        return {"status": "success", "data": {"id": data_id, **data}}

    def delete_normalized_data(self, data_id: str):
        """정규화 데이터 삭제"""
        return {"status": "success", "message": "deleted"}

    def get_metrics(self):
        """메트릭 조회"""
        return {"status": "success", "metrics": {}}

    # ===== AI 모델 Health Check 메서드들 =====

    def check_ai_model_health(self):
        """AI 모델 상태 확인"""
        try:
            # AI 모델 상태 확인
            model_status = self.service.check_ai_model_status()
            return {
                "status": "success",
                "ai_model": {
                    "status": model_status.get("status", "unknown"),
                    "model_name": model_status.get("model_name", "BOMI AI"),
                    "model_loaded": model_status.get("model_loaded", False),
                    "regulation_data_loaded": model_status.get("regulation_data_loaded", False),
                    "faiss_index_ready": model_status.get("faiss_index_ready", False),
                    "last_check": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI 모델 상태 확인 실패: {str(e)}",
                "ai_model": {
                    "status": "error",
                    "model_name": "BOMI AI",
                    "model_loaded": False,
                    "regulation_data_loaded": False,
                    "faiss_index_ready": False,
                    "last_check": datetime.now().isoformat()
                }
            }

    def get_ai_model_info(self):
        """AI 모델 상세 정보 조회"""
        try:
            model_info = self.service.get_ai_model_info()
            return {
                "status": "success",
                "model_info": model_info
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI 모델 정보 조회 실패: {str(e)}"
            }

    def test_ai_mapping(self, substance_name: str):
        """AI 모델 매핑 기능 테스트"""
        try:
            test_result = self.service.test_ai_mapping(substance_name)
            return {
                "status": "success",
                "test_result": test_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI 모델 매핑 테스트 실패: {str(e)}"
            }

    # ===== 협력사 ESG 데이터 관련 메서드 =====

    def upload_partner_esg_data(self, file, company_id: str = None):
        """협력사 ESG 데이터 파일 업로드 및 검증"""
        try:
            # 파일 검증
            if not file.filename:
                return {"status": "error", "message": "파일이 선택되지 않았습니다."}
            
            # 지원 파일 형식 검증
            allowed_extensions = ['.xlsx', '.xls', '.csv', '.pdf']
            file_extension = file.filename.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return {
                    "status": "error", 
                    "message": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
                }
            
            # 파일 업로드 처리
            result = self.service.upload_partner_esg_file(file, company_id)
            return {
                "status": "success",
                "message": "파일 업로드 완료",
                "data": {
                    "filename": file.filename,
                    "size": file.size,
                    "company_id": company_id,
                    "upload_id": result.get("upload_id"),
                    "validation_status": "pending"
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"파일 업로드 실패: {str(e)}"}

    def validate_partner_esg_data(self, data: dict):
        """협력사 ESG 데이터 검증 및 표준화"""
        try:
            validation_result = self.service.validate_partner_esg_data(data)
            return {
                "status": "success",
                "message": "데이터 검증 완료",
                "data": validation_result
            }
        except Exception as e:
            return {"status": "error", "message": f"데이터 검증 실패: {str(e)}"}

    def get_partner_dashboard(self, company_id: str):
        """협력사 ESG 자가진단 대시보드 데이터 조회"""
        try:
            dashboard_data = self.service.get_partner_dashboard_data(company_id)
            return {
                "status": "success",
                "data": dashboard_data
            }
        except Exception as e:
            return {"status": "error", "message": f"대시보드 데이터 조회 실패: {str(e)}"}

    def generate_partner_report(self, report_type: str, company_id: str):
        """협력사 ESG 보고서 자동 생성"""
        try:
            report_data = self.service.generate_partner_esg_report(report_type, company_id)
            return {
                "status": "success",
                "message": "보고서 생성 완료",
                "data": report_data
            }
        except Exception as e:
            return {"status": "error", "message": f"보고서 생성 실패: {str(e)}"}

    def get_esg_schema(self, industry: str):
        """업종별 ESG 데이터 스키마 조회"""
        try:
            schema = self.service.get_esg_schema_by_industry(industry)
            return {
                "status": "success",
                "data": schema
            }
        except Exception as e:
            return {"status": "error", "message": f"스키마 조회 실패: {str(e)}"}

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
