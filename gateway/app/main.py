# main.py (gateway)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx, os, logging
from app.domain.auth.router import router as auth_router

# ===== 환경변수 설정 =====
# 서비스 URL 설정 (Railway 실제 URL)
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "https://account-service-production-a0cc.up.railway.app")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "https://assessment-service-production-f3b1.up.railway.app")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "https://chatbot-service-production-fb76.up.railway.app")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://eripotter.com")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# 개발 환경에서는 docker-compose의 서비스 이름을 사용
if os.getenv("ENVIRONMENT") == "development":
    ACCOUNT_SERVICE_URL = "http://account-service:8001"
    ASSESSMENT_SERVICE_URL = "http://assessment-service:8002"
    CHATBOT_SERVICE_URL = "http://chatbot-service:8003"

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set")

# ===== 상수 설정 =====
TIMEOUT = 60000  # 60초
HEALTH_CHECK_TIMEOUT = 10  # 10초

# ===== 로깅 설정 =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(title="MSA API Gateway", version="1.0.0")

# Session 미들웨어 추가 (OAuth 상태 관리용)
app.add_middleware(
    SessionMiddleware, 
    secret_key=JWT_SECRET_KEY,
    same_site="lax",  # Railway는 HTTPS가 아닐 수 있음
    secure=False      # Railway는 HTTPS가 아닐 수 있음
)

# ===== CORS 설정 =====
WHITELIST = {
    "https://eripotter.com",
    "https://www.eripotter.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:3001",
    "https://accounts.google.com"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Railway 배포를 위해 임시로 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def cors_headers_for(request: Request):
    """요청 Origin이 화이트리스트에 있으면 해당 Origin을 그대로 반환."""
    origin = request.headers.get("origin", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Expose-Headers": "*"
    }

# 헬스체크 엔드포인트
@app.get("/health")
async def health():
    """Gateway와 필수 의존성(Account Service) 헬스체크."""
    try:
        # Account 서비스 헬스체크 - 필수 의존성
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            account_health = await client.get(f"{ACCOUNT_SERVICE_URL}/health")
            if account_health.status_code != 200:
                logger.error(f"Account service returned unhealthy status: {account_health.status_code}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "unhealthy",
                        "service": "gateway",
                        "error": "Account service is unhealthy",
                        "timestamp": logging.Formatter().converter()
                    }
                )
            
            # 모든 검사 통과
            return {
                "status": "healthy",
                "service": "gateway",
                "dependencies": {
                    "account": "healthy"
                },
                "timestamp": logging.Formatter().converter()
            }

    except Exception as e:
        logger.error(f"Account service health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "service": "gateway",
                "error": f"Failed to connect to account service: {str(e)}",
                "timestamp": logging.Formatter().converter()
            }
        )

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """CORS preflight 직접 처리."""
    return Response(status_code=204, headers=cors_headers_for(request))

# ---- 단일 프록시 유틸 ----
async def _proxy(request: Request, upstream_base: str, rest: str):
    url = upstream_base.rstrip("/") + "/" + rest.lstrip("/")
    logger.info(f"🔗 프록시 요청: {request.method} {request.url.path} -> {url}")

    # 원본 요청 복제
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    params = dict(request.query_params)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            upstream = await client.request(
                request.method, url, params=params, content=body, headers=headers
            )
            logger.info(f"✅ 프록시 응답: {upstream.status_code} {url}")
    except httpx.HTTPError as e:
        logger.error(f"❌ 프록시 HTTP 오류: {e} {url}")
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": str(e)},
            headers=cors_headers_for(request),
        )
    except Exception as e:
        logger.error(f"❌ 프록시 일반 오류: {e} {url}")
        return JSONResponse(
            status_code=500,
            content={"error": "Gateway Error", "detail": str(e)},
            headers=cors_headers_for(request),
        )

    # 업스트림 응답 전달
    passthrough = {}
    for k, v in upstream.headers.items():
        lk = k.lower()
        if lk in ("content-type", "set-cookie", "cache-control"):
            passthrough[k] = v

    # CORS 헤더를 명시적으로 덮어쓴다
    passthrough.update(cors_headers_for(request))

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=passthrough,
        media_type=upstream.headers.get("content-type"),
    )

# ---- account-service 프록시 ----
@app.api_route("/api/account/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def account_any(path: str, request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, path)

# ---- assessment-service 프록시 ----
@app.api_route("/api/assessment", methods=["GET","POST","PUT","PATCH","DELETE"])
async def assessment_root(request: Request):
    return await _proxy(request, ASSESSMENT_SERVICE_URL, "/assessment")

@app.api_route("/api/assessment/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def assessment_any(path: str, request: Request):
    return await _proxy(request, ASSESSMENT_SERVICE_URL, f"/assessment/{path}")

# ---- chatbot-service 프록시 ----
@app.api_route("/api/chatbot", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_root(request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, "/")

@app.api_route("/api/chatbot/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_any(path: str, request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, path)

# Auth 라우터 추가 (마지막에 추가하여 다른 라우터와 충돌 방지)
app.include_router(auth_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))