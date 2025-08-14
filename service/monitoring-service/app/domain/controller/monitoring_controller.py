class MonitoringController:
    def __init__(self, service):
        self.service = service

    def get_all_monitoring_data(self):
        """모든 모니터링 데이터 조회"""
        return {"status": "success", "data": []}

    def get_company_monitoring_data(self, company_id: str):
        """특정 회사 모니터링 데이터 조회"""
        return {"status": "success", "data": {"company_id": company_id}}

    def create_monitoring_data(self, monitoring_data: dict):
        """모니터링 데이터 생성"""
        return {"status": "success", "data": monitoring_data}

    def update_monitoring_data(self, company_id: str, monitoring_data: dict):
        """모니터링 데이터 업데이트"""
        return {"status": "success", "data": {"company_id": company_id, **monitoring_data}}

    def delete_monitoring_data(self, company_id: str):
        """모니터링 데이터 삭제"""
        return {"status": "success", "message": "deleted"}

    def get_metrics(self):
        """메트릭 조회"""
        return {"status": "success", "metrics": {}}
