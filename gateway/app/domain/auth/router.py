from fastapi import APIRouter, Request, HTTPException, status
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
import httpx
import os
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://eripotter.com")

# OAuth 클라이언트 초기화
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

async def verify_and_decode_token(token, request):
    """Google ID 토큰을 검증하고 디코드하는 함수"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        logger.info("Verifying Google ID token...")
        
        # Google의 공개 키로 토큰 검증
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        logger.info(f"Token verified successfully. User info: {json.dumps(idinfo, indent=2)}")
        
        # 토큰 발급자 확인
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.error("Wrong token issuer!")
            raise ValueError('Wrong issuer.')
            
        return idinfo
        
    except ImportError:
        logger.warning("Google Auth library not available, skipping token verification")
        # 토큰 검증을 건너뛰고 기본 처리
        return await oauth.google.parse_id_token(request, {"id_token": token})
    except ValueError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/google/login")
async def google_login(request: Request):
    try:
        redirect_uri = "https://gateway-production-5d19.up.railway.app/auth/google/callback"
        logger.info(f"Starting Google login with redirect_uri: {redirect_uri}")
        
        request.session['oauth_state'] = os.urandom(16).hex()
        logger.info(f"Generated OAuth state: {request.session['oauth_state']}")
        
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri,
            state=request.session['oauth_state']
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google/callback")
async def auth_callback(request: Request):
    try:
        logger.info("Received callback from Google")
        
        # state 검증
        state = request.query_params.get('state')
        stored_state = request.session.get('oauth_state')
        
        logger.info(f"Checking state - Received: {state}, Stored: {stored_state}")
        
        if not state or not stored_state or state != stored_state:
            logger.error(f"State mismatch: got {state}, expected {stored_state}")
            return RedirectResponse(url=f"{FRONTEND_URL}/?error=invalid_state")
        
        del request.session['oauth_state']
        logger.info("State verified and cleared from session")
        
        # 1. Google OAuth 토큰 얻기
        token = await oauth.google.authorize_access_token(request)
        logger.info("Got OAuth tokens from Google")
        logger.debug(f"Token response: {json.dumps(token, indent=2)}")
        
        # 2. ID 토큰 검증
        id_token_value = token.get('id_token')
        if not id_token_value:
            logger.error("No ID token in OAuth response")
            return RedirectResponse(url=f"{FRONTEND_URL}/?error=no_id_token")
            
        userinfo = await verify_and_decode_token(id_token_value, request)
        logger.info(f"Verified user email: {userinfo.get('email')}")
        
        # 3. Account 서비스로 인증 정보 전달
        async with httpx.AsyncClient() as client:
            account_url = f"{ACCOUNT_SERVICE_URL}/api/v1/accounts/auth/google"
            logger.info(f"Sending user info to account service: {account_url}")
            
            response = await client.post(
                account_url,
                json={
                    "sub": userinfo.get("sub"),
                    "email": userinfo.get("email"),
                    "name": userinfo.get("name"),
                    "picture": userinfo.get("picture"),
                    "hd": userinfo.get("hd"),  # Google Workspace 도메인
                    "email_verified": userinfo.get("email_verified")
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Account service error: {response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}/?error=account_service_error")
            
            logger.info("Successfully got response from account service")
            data = response.json()
            access_token = data.get("access_token")
            
            logger.info("Generated JWT token for user")
            
            # 4. 프론트엔드로 리다이렉트
            redirect_url = f"{FRONTEND_URL}/callback?token={access_token}"
            logger.info(f"Redirecting to frontend: {redirect_url}")
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?error=auth_failed"
        )