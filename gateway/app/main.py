from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="MSA API Gateway",
    description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI URL
    redoc_url="/redoc"  # ReDoc UI URL
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MSA API Gateway",
        version="1.0.0",
        description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
        routes=app.routes,
    )
    
    # 서버 정보 추가
    openapi_schema["servers"] = [
        {"url": "http://localhost:8080", "description": "Development server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 서비스 URL 매핑 (환경 변수에서 가져옴)
SERVICE_REGISTRY: Dict[str, str] = {
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
}

@app.get("/health", 
    summary="Health Check",
    description="게이트웨이 서비스의 상태를 확인합니다.",
    response_description="서비스가 정상적으로 동작 중임을 나타내는 응답",
    responses={
        200: {
            "description": "서비스가 정상 동작 중",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"}
                }
            }
        }
    }
)
async def health_check():
    """
    게이트웨이 서비스의 상태를 확인하는 엔드포인트입니다.
    """
    return {"status": "healthy"}

@app.api_route("/{service}/{path:path}", 
    methods=["GET", "POST", "PUT", "DELETE"],
    summary="서비스 프록시",
    description="요청을 적절한 마이크로서비스로 라우팅합니다.",
    response_description="대상 서비스의 응답을 그대로 반환",
    responses={
        404: {
            "description": "요청한 서비스를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "Service 'unknown' not found"}
                }
            }
        },
        503: {
            "description": "서비스가 현재 사용 불가능",
            "content": {
                "application/json": {
                    "example": {"detail": "Service 'user' is unavailable"}
                }
            }
        }
    }
)
async def proxy_request(
    service: str = Path(..., description="라우팅할 대상 서비스 이름 (예: user, product, order)"),
    path: str = Path(..., description="서비스의 세부 경로"),
    request: Request = Path(..., description="클라이언트의 원본 요청")
):
    if service not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    # 대상 서비스의 기본 URL 가져오기
    target_service_base_url = SERVICE_REGISTRY[service]
    
    # 전체 대상 URL 구성
    target_url = f"{target_service_base_url}/{path}"
    
    # 원본 요청에서 헤더와 쿼리 파라미터 복사
    headers = dict(request.headers)
    headers.pop("host", None)  # host 헤더 제거
    
    try:
        # 클라이언트 요청의 body 읽기
        body = await request.body()
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.content else None,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service '{service}' is unavailable")

# 프론트엔드에서 받을 데이터 모델 정의
class UserInput(BaseModel):
    type: str
    content: str
    timestamp: str

@app.post("/api/user-input", 
    summary="사용자 입력 처리",
    description="프론트엔드에서 전송된 사용자 입력을 처리합니다.",
    response_description="처리 결과",
    responses={
        200: {
            "description": "입력 처리 성공",
            "content": {
                "application/json": {
                    "example": {"status": "success", "message": "입력이 처리되었습니다."}
                }
            }
        }
    }
)
async def handle_user_input(user_input: UserInput):
    """
    프론트엔드에서 전송된 사용자 입력을 처리하는 엔드포인트입니다.
    """
    print("받은 사용자 입력:")
    print(f"타입: {user_input.type}")
    print(f"내용: {user_input.content}")
    print(f"시간: {user_input.timestamp}")
    
    return {"status": "success", "message": "입력이 처리되었습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)