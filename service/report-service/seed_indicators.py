"""
지표 데이터 시드 스크립트
"""
import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.domain.entity.report_entity import Indicator
from eripotter_common.database import get_session

def seed_indicators():
    """테스트용 지표 데이터 생성"""
    
    indicators = [
        {
            "indicator_id": "KBZ-EN22",
            "title": "온실가스 배출량",
            "category": "Environmental",
            "subcategory": "Climate Change",
            "description": "회사의 온실가스 배출량을 측정하고 보고하는 지표",
            "input_fields": {
                "scope1_emissions": {"type": "number", "description": "Scope 1 온실가스 배출량 (tCO2e)", "required": True},
                "scope2_emissions": {"type": "number", "description": "Scope 2 온실가스 배출량 (tCO2e)", "required": True},
                "scope3_emissions": {"type": "number", "description": "Scope 3 온실가스 배출량 (tCO2e)", "required": False},
                "emission_reduction_target": {"type": "number", "description": "온실가스 감축 목표 (%)", "required": False},
                "reduction_measures": {"type": "text", "description": "감축 조치 내용", "required": False}
            },
            "example_data": {
                "scope1_emissions": 1500,
                "scope2_emissions": 3000,
                "scope3_emissions": 8000,
                "emission_reduction_target": 30,
                "reduction_measures": "재생에너지 도입, 에너지 효율 개선"
            }
        },
        {
            "indicator_id": "KBZ-EN23",
            "title": "에너지 사용량",
            "category": "Environmental",
            "subcategory": "Energy",
            "description": "회사의 에너지 사용량 및 효율성 지표",
            "input_fields": {
                "total_energy_consumption": {"type": "number", "description": "총 에너지 사용량 (MWh)", "required": True},
                "renewable_energy_ratio": {"type": "number", "description": "재생에너지 비율 (%)", "required": True},
                "energy_efficiency_improvement": {"type": "number", "description": "에너지 효율 개선률 (%)", "required": False},
                "energy_saving_measures": {"type": "text", "description": "에너지 절약 조치", "required": False}
            },
            "example_data": {
                "total_energy_consumption": 50000,
                "renewable_energy_ratio": 25,
                "energy_efficiency_improvement": 15,
                "energy_saving_measures": "LED 조명 교체, 스마트 빌딩 시스템 도입"
            }
        },
        {
            "indicator_id": "KBZ-SO1",
            "title": "직원 안전 및 건강",
            "category": "Social",
            "subcategory": "Labor Rights",
            "description": "직원의 안전과 건강을 보호하기 위한 지표",
            "input_fields": {
                "workplace_accidents": {"type": "number", "description": "직장 내 사고 건수", "required": True},
                "lost_time_injury_rate": {"type": "number", "description": "근로손실 재해율", "required": True},
                "health_safety_training_hours": {"type": "number", "description": "안전보건 교육 시간", "required": False},
                "occupational_health_programs": {"type": "text", "description": "직업건강 프로그램", "required": False}
            },
            "example_data": {
                "workplace_accidents": 5,
                "lost_time_injury_rate": 0.8,
                "health_safety_training_hours": 24,
                "occupational_health_programs": "정기 건강검진, 스트레스 관리 프로그램"
            }
        },
        {
            "indicator_id": "KBZ-GO1",
            "title": "이사회 구성 및 독립성",
            "category": "Governance",
            "subcategory": "Board Structure",
            "description": "이사회의 구성과 독립성을 평가하는 지표",
            "input_fields": {
                "board_size": {"type": "number", "description": "이사회 구성원 수", "required": True},
                "independent_directors": {"type": "number", "description": "사외이사 수", "required": True},
                "independent_director_ratio": {"type": "number", "description": "사외이사 비율 (%)", "required": True},
                "board_diversity": {"type": "text", "description": "이사회 다양성 현황", "required": False},
                "board_meeting_attendance": {"type": "number", "description": "이사회 출석률 (%)", "required": False}
            },
            "example_data": {
                "board_size": 9,
                "independent_directors": 6,
                "independent_director_ratio": 67,
                "board_diversity": "성별 다양성 33%, 전문성 다양성 확보",
                "board_meeting_attendance": 95
            }
        }
    ]
    
    try:
        with get_session() as db:
            created_count = 0
            for indicator_data in indicators:
                # 기존 지표 확인
                existing = db.query(Indicator).filter(Indicator.indicator_id == indicator_data["indicator_id"]).first()
                
                if existing:
                    print(f"지표 {indicator_data['indicator_id']} 이미 존재함 - 업데이트")
                    # 기존 데이터 업데이트
                    for key, value in indicator_data.items():
                        if key != "indicator_id":  # ID는 변경하지 않음
                            setattr(existing, key, value)
                else:
                    print(f"지표 {indicator_data['indicator_id']} 생성")
                    # 새 지표 생성
                    indicator = Indicator(**indicator_data)
                    db.add(indicator)
                    created_count += 1
            
            db.commit()
            print(f"✅ {created_count}개의 새 지표가 생성되었습니다.")
            print(f"총 {len(indicators)}개의 지표 데이터가 준비되었습니다.")
            
    except Exception as e:
        print(f"❌ 지표 데이터 생성 실패: {e}")
        db.rollback()
        raise

if __name__ == "__main__":
    print("🌱 지표 데이터 시드 시작...")
    seed_indicators()
    print("✅ 지표 데이터 시드 완료!")
