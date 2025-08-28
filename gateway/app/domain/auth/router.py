from fastapi import APIRouter, Request, HTTPException, status
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
import httpx
import os

router = APIRouter()

# OAuth 설정
config = Config('.env')
oauth = OAuth(config)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://eripotter.com")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("Missing Google OAuth credentials")

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/auth/google/login")
async def google_login(request: Request):
    # Gateway의 콜백 URL 사용
    redirect_uri = f"{request.base_url}api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def auth_callback(request: Request):
    try:
        # 1. Google OAuth 토큰 얻기
        token = await oauth.google.authorize_access_token(request)
        userinfo = await oauth.google.parse_id_token(request, token)
        
        # 2. Account 서비스로 인증 정보 전달
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/auth/google",  # account_router의 auth 엔드포인트
                json={
                    "sub": userinfo.get("sub"),
                    "email": userinfo.get("email"),
                    "name": userinfo.get("name"),
                    "picture": userinfo.get("picture")
                }
            )
            
            if response.status_code != 200:
                print(f"Account service error: {response.text}")  # 디버깅용
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Account service error"
                )
            
            # 3. Account 서비스에서 받은 JWT 토큰으로 프론트엔드 리다이렉트
            data = response.json()
            access_token = data.get("access_token")
            
            # 4. 프론트엔드로 리다이렉트 (JWT 토큰과 함께)
            redirect_url = f"{FRONTEND_URL}/company-profile?token={access_token}"
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        print(f"OAuth callback error: {str(e)}")  # 디버깅용
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=auth_failed"
        )