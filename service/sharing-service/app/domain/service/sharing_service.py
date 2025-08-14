class SharingService:
    def __init__(self):
        pass

    def get_all_sharing_requests(self):
        """모든 데이터 공유 요청 목록 조회"""
        return []

    def get_sharing_request_by_id(self, request_id: str):
        """특정 데이터 공유 요청 조회"""
        return {"id": request_id}

    def create_sharing_request(self, request_data: dict):
        """데이터 공유 요청 생성"""
        return request_data

    def approve_sharing_request(self, request_id: str):
        """데이터 공유 요청 승인"""
        return {"request_id": request_id, "status": "approved"}

    def reject_sharing_request(self, request_id: str):
        """데이터 공유 요청 거부"""
        return {"request_id": request_id, "status": "rejected"}

    def send_approved_data(self, request_id: str):
        """승인된 데이터 전송"""
        return {"request_id": request_id, "status": "sent"}

    def get_supplier_chain(self, chain_level: int):
        """특정 차수 협력사 체인 조회"""
        return {"chain_level": chain_level, "suppliers": []}

    def get_metrics(self):
        """메트릭 조회"""
        return {}
