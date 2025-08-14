"""
Chatbot Service - LangChain 통합 서비스
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
from dotenv import load_dotenv
import uvicorn

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("chatbot-service")

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="Chatbot Service",
    description="LangChain 기반 챗봇 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eripotter.com",
        "https://www.eripotter.com",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangChain 모델 초기화
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. 기본 응답을 사용합니다.")
        llm = None
        embeddings = None
    else:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=openai_api_key
        )
        embeddings = OpenAIEmbeddings(
            api_key=openai_api_key
        )
except Exception as e:
    logger.error(f"LangChain 모델 초기화 실패: {str(e)}")
    llm = None
    embeddings = None

# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    company_id: Optional[str] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None

class DocumentUploadRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    company_id: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str
    message: str

# 기본 프롬프트 템플릿
DEFAULT_PROMPT = ChatPromptTemplate.from_template(
    """당신은 기업을 위한 전문적인 AI 어시스턴트 '애리'입니다.
    
    사용자 질문: {question}
    
    다음 지침을 따라 답변해주세요:
    1. 전문적이고 정확한 정보를 제공하세요
    2. 한국어로 답변하세요
    3. 필요시 구체적인 예시를 들어 설명하세요
    4. 기업 환경에 적합한 조언을 제공하세요
    
    답변:"""
)

# 기본 체인
if llm:
    basic_chain = DEFAULT_PROMPT | llm | StrOutputParser()
else:
    basic_chain = None

@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "chatbot"}

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Chatbot Service is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """기본 채팅 기능"""
    try:
        logger.info(f"Chat request from user: {request.user_id}")
        
        if not basic_chain:
            # OpenAI API 키가 없을 때 기본 응답
            return ChatResponse(
                response="안녕하세요! 현재 AI 서비스가 준비 중입니다. 잠시 후 다시 시도해주세요.",
                confidence=0.5
            )
        
        # 기본 체인 실행
        response = basic_chain.invoke({"question": request.message})
        
        return ChatResponse(
            response=response,
            confidence=0.8
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/chat/contextual", response_model=ChatResponse)
async def contextual_chat(request: ChatRequest):
    """컨텍스트를 고려한 채팅"""
    try:
        logger.info(f"Contextual chat request from user: {request.user_id}")
        
        if not llm:
            return ChatResponse(
                response="안녕하세요! 현재 AI 서비스가 준비 중입니다. 잠시 후 다시 시도해주세요.",
                confidence=0.5
            )
        
        # 컨텍스트가 있는 경우 프롬프트 수정
        if request.context:
            contextual_prompt = ChatPromptTemplate.from_template(
                """당신은 기업을 위한 전문적인 AI 어시스턴트입니다.
                
                컨텍스트 정보: {context}
                
                사용자 질문: {question}
                
                위 컨텍스트를 참고하여 답변해주세요. 한국어로 전문적이고 정확한 정보를 제공하세요.
                
                답변:"""
            )
            chain = contextual_prompt | llm | StrOutputParser()
            response = chain.invoke({
                "context": request.context,
                "question": request.message
            })
        else:
            response = basic_chain.invoke({"question": request.message})
        
        return ChatResponse(
            response=response,
            confidence=0.85
        )
        
    except Exception as e:
        logger.error(f"Contextual chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"컨텍스트 채팅 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(request: DocumentUploadRequest):
    """문서 업로드 및 벡터화"""
    try:
        logger.info(f"Document upload request for company: {request.company_id}")
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        documents = text_splitter.split_text(request.content)
        
        # 메타데이터 추가
        docs = [
            Document(
                page_content=doc,
                metadata=request.metadata or {}
            ) for doc in documents
        ]
        
        # 벡터 스토어 생성 (실제 구현에서는 영구 저장소 사용)
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings
        )
        
        return DocumentResponse(
            document_id=f"doc_{len(docs)}",
            message=f"{len(docs)}개의 문서 청크가 성공적으로 업로드되었습니다."
        )
        
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 중 오류가 발생했습니다: {str(e)}")

@app.post("/chat/rag", response_model=ChatResponse)
async def rag_chat(request: ChatRequest):
    """RAG (Retrieval-Augmented Generation) 채팅"""
    try:
        logger.info(f"RAG chat request from user: {request.user_id}")
        
        # 실제 구현에서는 사용자/회사별 벡터 스토어에서 검색
        # 여기서는 기본 응답으로 대체
        
        rag_prompt = ChatPromptTemplate.from_template(
            """당신은 기업 문서를 기반으로 답변하는 AI 어시스턴트입니다.
            
            검색된 관련 문서:
            {context}
            
            사용자 질문: {question}
            
            위 문서를 참고하여 정확하고 유용한 답변을 제공하세요.
            문서에 없는 정보는 명시적으로 언급하세요.
            
            답변:"""
        )
        
        # 실제 구현에서는 벡터 검색 결과를 context에 넣어야 함
        mock_context = "관련 문서를 찾을 수 없습니다. 일반적인 조언을 제공합니다."
        
        chain = rag_prompt | llm | StrOutputParser()
        response = chain.invoke({
            "context": mock_context,
            "question": request.message
        })
        
        return ChatResponse(
            response=response,
            sources=["문서 검색 기능은 개발 중입니다"],
            confidence=0.7
        )
        
    except Exception as e:
        logger.error(f"RAG chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG 채팅 처리 중 오류가 발생했습니다: {str(e)}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """요청 로깅 미들웨어"""
    logger.info(f"📥 요청: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 응답: {response.status_code}")
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    logger.info(f"🤖 챗봇 서비스 시작 - 포트: {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
