class NormalService:
    def __init__(self):
        pass

    def get_all_normalized_data(self):
        """모든 정규화 데이터 조회"""
        return []

    def get_normalized_data_by_id(self, data_id: str):
        """특정 정규화 데이터 조회"""
        return {"id": data_id}

    def upload_and_normalize_excel(self, file):
        """엑셀 파일 업로드 및 정규화"""
        return {"filename": file.filename, "status": "uploaded"}

    def create_normalized_data(self, data: dict):
        """정규화 데이터 생성"""
        return data

    def update_normalized_data(self, data_id: str, data: dict):
        """정규화 데이터 업데이트"""
        return {"id": data_id, **data}

    def delete_normalized_data(self, data_id: str):
        """정규화 데이터 삭제"""
        return True

    def get_metrics(self):
        """메트릭 조회"""
        return {}
