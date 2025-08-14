class MonitoringService:
    def __init__(self):
        pass

    def get_all_monitoring_data(self):
        """모든 모니터링 데이터 조회"""
        return []

    def get_company_monitoring_data(self, company_id: str):
        """특정 회사 모니터링 데이터 조회"""
        return {"company_id": company_id}

    def create_monitoring_data(self, monitoring_data: dict):
        """모니터링 데이터 생성"""
        return monitoring_data

    def update_monitoring_data(self, company_id: str, monitoring_data: dict):
        """모니터링 데이터 업데이트"""
        return {"company_id": company_id, **monitoring_data}

    def delete_monitoring_data(self, company_id: str):
        """모니터링 데이터 삭제"""
        return True

    def get_metrics(self):
        """메트릭 조회"""
        return {}
