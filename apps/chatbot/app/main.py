"""이음 RAG 챗봇 — FastAPI 엔트리포인트 (규현).

딸기 농약 로테이션 추천 + REI 관련 정보 Q&A.
현재는 뼈대: /chat 은 rag.answer() 를 호출하며, RAG 미구성 시 폴백 응답.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag import answer

app = FastAPI(title="Ieum Chatbot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용. 배포 시 웹 도메인으로 제한
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    crop: str | None = None  # 예: "strawberry"


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = answer(req.message, crop=req.crop)
    return ChatResponse(answer=result["answer"], sources=result.get("sources", []))
