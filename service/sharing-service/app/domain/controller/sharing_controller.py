class SharingController:
    def __init__(self, service):
        self.service = service

    def get_all_sharing_requests(self):
        """모든 데이터 공유 요청 목록 조회"""
        return {"status": "success", "data": []}

    def get_sharing_request_by_id(self, request_id: str):
        """특정 데이터 공유 요청 조회"""
        return {"status": "success", "data": {"id": request_id}}

    def create_sharing_request(self, request_data: dict):
        """데이터 공유 요청 생성"""
        return {"status": "success", "data": request_data}

    def approve_sharing_request(self, request_id: str):
        """데이터 공유 요청 승인"""
        return {"status": "success", "message": "approved", "request_id": request_id}

    def reject_sharing_request(self, request_id: str):
        """데이터 공유 요청 거부"""
        return {"status": "success", "message": "rejected", "request_id": request_id}

    def send_approved_data(self, request_id: str):
        """승인된 데이터 전송"""
        return {"status": "success", "message": "data sent", "request_id": request_id}

    def get_supplier_chain(self, chain_level: int):
        """특정 차수 협력사 체인 조회"""
        return {"status": "success", "chain_level": chain_level, "suppliers": []}

    def get_metrics(self):
        """메트릭 조회"""
        return {"status": "success", "metrics": {}}
