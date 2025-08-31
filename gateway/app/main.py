from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx
import os
import logging
from app.domain.auth.router import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(title="MSA API Gateway", version="1.0.0")

# Session 미들웨어 추가 (OAuth 상태 관리용)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=3600,  # 1시간
    same_site="lax",
    https_only=True
)

# CORS 설정
WHITELIST = {
    "https://eripotter.com",
    "https://www.eripotter.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "https://accounts.google.com"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(WHITELIST),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cors_headers_for(request: Request):
    origin = request.headers.get("origin")
    if origin in WHITELIST:
        return {
            "Access-Control-Allow-Origin": origin,
            "Vary": "Origin",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
        }
    return {}

# 서비스 URL 설정
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:8002")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8003")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://localhost:8007")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "20"))

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "gateway"}

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return Response(status_code=204, headers=cors_headers_for(request))

async def _proxy(request: Request, upstream_base: str, rest: str):
    url = upstream_base.rstrip("/") + "/" + rest.lstrip("/")
    logger.info(f"🔗 프록시 요청: {request.method} {request.url.path} -> {url}")
    logger.info(f"📝 상세 정보: upstream_base={upstream_base}, rest={rest}")

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

    passthrough = {}
    for k, v in upstream.headers.items():
        lk = k.lower()
        if lk in ("content-type", "set-cookie", "cache-control"):
            passthrough[k] = v

    passthrough.update(cors_headers_for(request))

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=passthrough,
        media_type=upstream.headers.get("content-type"),
    )

@app.api_route("/api/account/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def account_any(path: str, request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, path)

@app.api_route("/api/assessment", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def assessment_root(request: Request):
    return await _proxy(request, ASSESSMENT_SERVICE_URL, "/assessment")

@app.api_route("/api/assessment/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def assessment_any(path: str, request: Request):
    return await _proxy(request, ASSESSMENT_SERVICE_URL, f"/assessment/{path}")

@app.api_route("/api/chatbot", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def chatbot_root(request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, "/")

@app.api_route("/api/chatbot/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def chatbot_any(path: str, request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, path)

@app.api_route("/api/report", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def report_root(request: Request):
    return await _proxy(request, REPORT_SERVICE_URL, "/")

@app.api_route("/api/report/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def report_any(path: str, request: Request):
    return await _proxy(request, REPORT_SERVICE_URL, path)

# Auth 라우터를 두 경로에 마운트
app.include_router(auth_router, prefix="/api/auth")  # 프론트엔드 API 요청용
app.include_router(auth_router, prefix="/auth")      # Google 콜백용

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))