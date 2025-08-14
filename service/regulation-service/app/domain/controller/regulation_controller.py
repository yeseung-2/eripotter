class RegulationController:
    def __init__(self, service):
        self.service = service

    def get_all_regulations(self):
        """모든 규정안 목록 조회"""
        return {"status": "success", "data": []}

    def get_regulation_by_id(self, regulation_id: str):
        """특정 규정안 조회"""
        return {"status": "success", "data": {"id": regulation_id}}

    def create_regulation(self, regulation_data: dict):
        """규정안 생성"""
        return {"status": "success", "data": regulation_data}

    def update_regulation(self, regulation_id: str, regulation_data: dict):
        """규정안 업데이트"""
        return {"status": "success", "data": {"id": regulation_id, **regulation_data}}

    def delete_regulation(self, regulation_id: str):
        """규정안 삭제"""
        return {"status": "success", "message": "deleted"}

    def get_metrics(self):
        """메트릭 조회"""
        return {"status": "success", "metrics": {}}
