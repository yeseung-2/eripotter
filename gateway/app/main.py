# main.py (gateway) — 깔끔 버전
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
import httpx, os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(title="MSA API Gateway", version="1.0.0")

# CORS: 운영 도메인만 허용 (+개발용은 필요시 추가)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sme.eripotter.com",
        # "http://localhost:8080", "http://localhost:3000"  # 개발용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8003")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "20"))

@app.get("/health")
async def health(): return {"status": "healthy", "service": "gateway"}

@app.options("/{path:path}")
async def options_handler(path: str):
    """CORS preflight 요청 처리"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "https://sme.eripotter.com",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

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
    except Exception as e:
        logger.error(f"❌ 프록시 오류: {str(e)} {url}")
        raise

    # 응답 그대로 전달(바이너리/JSON 모두 대응)
    # 보안상 필요한 헤더만 복사
    passthrough = {}
    for k, v in upstream.headers.items():
        lk = k.lower()
        if lk in ("content-type", "set-cookie", "cache-control", "access-control-allow-origin", "access-control-allow-methods", "access-control-allow-headers"):
            passthrough[k] = v

    # CORS 헤더 명시적 추가 (프록시 응답에)
    passthrough["Access-Control-Allow-Origin"] = "https://sme.eripotter.com"
    passthrough["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    passthrough["Access-Control-Allow-Headers"] = "*"
    passthrough["Access-Control-Allow-Credentials"] = "true"

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=passthrough,
        media_type=upstream.headers.get("content-type")
    )

# ---- account-service 프록시 ----
@app.api_route("/api/account", methods=["GET","POST","PUT","PATCH","DELETE"])
async def account_root(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/")

@app.api_route("/api/account/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def account_any(path: str, request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, path)

# ---- chatbot-service 프록시 ----
@app.api_route("/api/chatbot", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_root(request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, "/")

@app.api_route("/api/chatbot/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_any(path: str, request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, path)

if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))