from pydantic import BaseModel
from typing import Optional

class LoginData(BaseModel):
    user_id: str
    user_pw: str

class SignupData(BaseModel):
    user_id: str
    user_pw: str
    industry: str
    bs_num: str
    company_id: str
    company_add: str
    company_country: str
    manager_dept: str
    manager_name: str
    manager_email: str
    manager_phone: str

class AccountResponse(BaseModel):
    status: str
    message: str
    user_id: str
    company_id: Optional[str] = None
    user_name: Optional[str] = None
    user: Optional[dict] = None
