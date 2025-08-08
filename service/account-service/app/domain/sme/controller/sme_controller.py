import logging

logger = logging.getLogger(__name__)

class SmeController:
    def __init__(self):
        pass
    
    def get_sample_data(self):
        """
        샘플 데이터를 반환합니다.
        """
        return {
            "message": "SME Controller is working",
            "status": "success"
        }