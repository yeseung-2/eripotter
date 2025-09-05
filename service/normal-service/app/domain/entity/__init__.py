"""
Entity 모듈 - SQLAlchemy 모델들
"""

from .normal_entity import NormalEntity, Base
from .certification_entity import CertificationEntity

__all__ = [
    'Base',
    'NormalEntity', 
    'CertificationEntity'
]
