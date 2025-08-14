class ReportService:
    def __init__(self):
        pass

    def get_all_reports(self):
        """모든 보고서 목록 조회"""
        return []

    def get_report_by_id(self, report_id: str):
        """특정 보고서 조회"""
        return {"id": report_id}

    def create_report_draft(self, report_data: dict):
        """보고서 초안 생성"""
        return report_data

    def update_report(self, report_id: str, report_data: dict):
        """보고서 업데이트"""
        return {"id": report_id, **report_data}

    def delete_report(self, report_id: str):
        """보고서 삭제"""
        return True

    def generate_report_with_ai(self, report_id: str):
        """AI를 통한 보고서 초안 생성"""
        return {"report_id": report_id, "status": "generating"}

    def get_metrics(self):
        """메트릭 조회"""
        return {}
