from fastapi import APIRouter, Request, HTTPException, status
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
import httpx
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth 설정
config = Config('.env')
oauth = OAuth(config)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://eripotter.com")
GATEWAY_URL = "https://gateway-production-5d19.up.railway.app"  # 고정 URL 사용

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

@router.get("/google/login")
async def google_login(request: Request):
    try:
        redirect_uri = f"{GATEWAY_URL}/auth/google/callback"
        logger.info(f"Starting Google login with redirect_uri: {redirect_uri}")
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google/callback")
async def auth_callback(request: Request):
    try:
        logger.info("Received callback from Google")
        # 1. Google OAuth 토큰 얻기
        token = await oauth.google.authorize_access_token(request)
        logger.info("Got access token from Google")
        
        userinfo = await oauth.google.parse_id_token(request, token)
        logger.info(f"Got user info: {userinfo.get('email')}")
        
        # 2. Account 서비스로 인증 정보 전달
        async with httpx.AsyncClient() as client:
            account_url = f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/auth/google"
            logger.info(f"Sending request to account service: {account_url}")
            
            response = await client.post(
                account_url,
                json={
                    "sub": userinfo.get("sub"),
                    "email": userinfo.get("email"),
                    "name": userinfo.get("name"),
                    "picture": userinfo.get("picture")
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Account service error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Account service error"
                )
            
            logger.info("Successfully got response from account service")
            data = response.json()
            access_token = data.get("access_token")
            
            # 4. 프론트엔드로 리다이렉트
            redirect_url = f"{FRONTEND_URL}/auth/google/callback?token={access_token}"
            logger.info(f"Redirecting to frontend: {redirect_url}")
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=auth_failed"
        )