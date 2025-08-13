from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountEntity(Base):
    __tablename__ = "account"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    user_pw = Column(String, nullable=False)
    company_id = Column(String, nullable=False)
