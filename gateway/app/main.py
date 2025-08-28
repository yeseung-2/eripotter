# main.py (gateway) — CORS 보강 버전
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx, os, logging
from app.domain.auth.router import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(title="MSA API Gateway", version="1.0.0")

# Session 미들웨어 추가 (OAuth 상태 관리용)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET_KEY"))

# ===== CORS 설정 =====
WHITELIST = {
            "https://eripotter.com",
        "https://www.eripotter.com",              # www 도메인도 허용
    "http://localhost:3000", "http://localhost:5173","http://localhost:3001"  # 로컬 개발
    # "https://sme-eripotter-com.vercel.app",     # Vercel 프리뷰를 쓰면 주석 해제
}

# 미들웨어(기본 방어막) - allow_origins는 넓게 두되 credentials 고려
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(WHITELIST),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cors_headers_for(request: Request):
    """요청 Origin이 화이트리스트에 있으면 해당 Origin을 그대로 반환."""
    origin = request.headers.get("origin")
    if origin in WHITELIST:
        return {
            "Access-Control-Allow-Origin": origin,
            "Vary": "Origin",  # 캐시 안정성
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
        }
    # 화이트리스트 밖이면 CORS 헤더 미부착(브라우저가 차단)
    return {}

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:8002")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8003")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "20"))

@app.get("/health")
async def health(): 
    return {"status": "healthy", "service": "gateway"}

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """CORS preflight 직접 처리(필요 시)."""
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
        # 예외가 나도 CORS 헤더는 항상 달아준다
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

    # CORS 헤더를 명시적으로 덮어쓴다(항상 부착)
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
    # /api/account/signup -> /signup로 변환
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