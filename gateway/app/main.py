# main.py (gateway)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx, os, logging
from datetime import datetime, timezone
from app.domain.auth.router import router as auth_router

def now_iso():
    return datetime.now(timezone.utc).isoformat()

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
TIMEOUT = 60  # 60초
HEALTH_CHECK_TIMEOUT = 10  # 10초

# 타임아웃 관련 상세 설정
CONNECT_TIMEOUT = 5  # 연결 타임아웃 5초
READ_TIMEOUT = TIMEOUT  # 읽기 타임아웃은 전체 타임아웃과 동일하게

# ===== 로깅 설정 =====
import json
from time import time
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": now_iso(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "gateway"
        }
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "error"):
            log_data["error"] = str(record.error)
        return json.dumps(log_data)

# JSON 형식 로깅 설정
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("gateway")

app = FastAPI(title="MSA API Gateway", version="1.0.0")

# 헬스체크 엔드포인트를 먼저 등록
@app.get("/livez", methods=["GET", "HEAD"])
async def livez():
    """프로세스 생존 여부만 확인 (Railway Healthcheck용)"""
    return {
        "status": "alive",
        "service": "gateway",
        "timestamp": now_iso(),
    }

# Session 미들웨어는 JWT_SECRET_KEY가 있을 때만 추가
if JWT_SECRET_KEY:
    app.add_middleware(
        SessionMiddleware, 
        secret_key=JWT_SECRET_KEY,
        same_site="lax",  # Railway는 HTTPS가 아닐 수 있음
        secure=False      # Railway는 HTTPS가 아닐 수 있음
    )
else:
    logger.warning("JWT_SECRET_KEY not set - session middleware disabled")

# ===== CORS 설정 =====
WHITELIST = {
    "https://eripotter.com",
    "https://www.eripotter.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:3001",
    "https://accounts.google.com"
}

# 개발 환경에서는 모든 origin 허용
if os.getenv("ENVIRONMENT") == "development":
    CORS_ORIGINS = ["*"]
    logger.warning("개발 환경: 모든 CORS origin 허용")
else:
    CORS_ORIGINS = list(WHITELIST)
    logger.info(f"프로덕션 환경: CORS whitelist 적용 ({len(CORS_ORIGINS)}개 도메인)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin", 
        "X-Requested-With",
        "X-Request-ID"
    ],
    expose_headers=[
        "Content-Length",
        "Content-Type",
        "X-Request-ID"
    ]
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
@app.get("/livez")
async def livez():
    """프로세스 생존 여부만 확인 (Railway Healthcheck용)"""
    return {
        "status": "alive",
        "service": "gateway",
        "timestamp": now_iso(),
    }

@app.get("/readyz")
async def readyz():
    """의존성 서비스(Account Service) 준비 상태 확인"""
    try:
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            r = await client.get(f"{ACCOUNT_SERVICE_URL}/health")
            if r.status_code != 200:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unready",
                        "service": "gateway",
                        "dependencies": {"account": "unhealthy"},
                        "timestamp": now_iso(),
                    },
                )
        return {
            "status": "ready",
            "service": "gateway",
            "dependencies": {"account": "healthy"},
            "timestamp": now_iso(),
        }
    except Exception as e:
        logger.error(f"Account service readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unready",
                "service": "gateway",
                "error": f"account check failed: {str(e)}",
                "timestamp": now_iso(),
            },
        )

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
                        "timestamp": now_iso()
                    }
                )
            
            # 모든 검사 통과
            return {
                "status": "healthy",
                "service": "gateway",
                "dependencies": {
                    "account": "healthy"
                },
                "timestamp": now_iso()
            }

    except Exception as e:
        logger.error(f"Account service health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "service": "gateway",
                "error": f"Failed to connect to account service: {str(e)}",
                "timestamp": now_iso()
            }
        )

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """CORS preflight 직접 처리."""
    return Response(status_code=204, headers=cors_headers_for(request))

# ---- 단일 프록시 유틸 ----
async def _proxy(request: Request, upstream_base: str, rest: str):
    url = upstream_base.rstrip("/") + "/" + rest.lstrip("/")
    start_time = time()
    request_id = request.headers.get("X-Request-ID", "-")
    
    logger.info(f"프록시 요청 시작", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "upstream_url": url
    })

    # 원본 요청 복제
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    params = dict(request.query_params)

    try:
        timeout_settings = httpx.Timeout(
            connect=CONNECT_TIMEOUT,
            read=READ_TIMEOUT,
            write=TIMEOUT,
            pool=TIMEOUT
        )
        async with httpx.AsyncClient(timeout=timeout_settings, follow_redirects=True) as client:
            upstream = await client.request(
                request.method, url, params=params, content=body, headers=headers
            )
            duration = int((time() - start_time) * 1000)
            logger.info("프록시 요청 완료", extra={
                "request_id": request_id,
                "status_code": upstream.status_code,
                "duration_ms": duration,
                "upstream_url": url
            })
            
    except httpx.TimeoutException as e:
        logger.error("프록시 타임아웃", extra={
            "request_id": request_id,
            "error": str(e),
            "upstream_url": url,
            "duration_ms": int((time() - start_time) * 1000)
        })
        return JSONResponse(
            status_code=504,
            content={"error": "Gateway Timeout", "detail": str(e)},
            headers=cors_headers_for(request),
        )
    except httpx.ConnectError as e:
        logger.error("프록시 연결 실패", extra={
            "request_id": request_id,
            "error": str(e),
            "upstream_url": url
        })
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": "서비스 연결 실패"},
            headers=cors_headers_for(request),
        )
    except httpx.HTTPError as e:
        logger.error("프록시 HTTP 오류", extra={
            "request_id": request_id,
            "error": str(e),
            "upstream_url": url
        })
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": str(e)},
            headers=cors_headers_for(request),
        )
    except Exception as e:
        logger.error("프록시 처리 실패", extra={
            "request_id": request_id,
            "error": str(e),
            "upstream_url": url
        })
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Gateway Error", "detail": "내부 처리 오류"},
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