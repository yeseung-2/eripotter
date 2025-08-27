class AssessmentController:
    def __init__(self, service):
        self.service = service

    def get_all_assessments(self):
        """모든 assessment 조회"""
        return {"status": "success", "data": []}

    def get_assessment_by_id(self, assessment_id: str):
        """특정 assessment 조회"""
        return {"status": "success", "data": {"id": assessment_id}}

    def create_assessment(self, assessment_data: dict):
        """assessment 생성"""
        return {"status": "success", "data": assessment_data}

    def update_assessment(self, assessment_id: str, assessment_data: dict):
        """assessment 업데이트"""
        return {"status": "success", "data": {"id": assessment_id, **assessment_data}}

    def delete_assessment(self, assessment_id: str):
        """assessment 삭제"""
        return {"status": "success", "message": "deleted"}

    def get_metrics(self):
        """메트릭 조회"""
        return {"status": "success", "metrics": {}}
