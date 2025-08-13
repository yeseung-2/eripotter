from pydantic import BaseModel

class LoginData(BaseModel):
    user_id: str
    user_pw: str

class SignupData(BaseModel):
    user_id: str
    user_pw: str
    company_id: str

class AccountResponse(BaseModel):
    status: str
    message: str
    user_id: str
    company_id: str
