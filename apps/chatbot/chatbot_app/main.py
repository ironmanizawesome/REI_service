"""이음 RAG 챗봇 — FastAPI 엔트리포인트 (규현).

프론트(중간발표 목업) 흐름 대응 백엔드:
  POST /rei      — (농약/성분 × 작물 × 작업유형 × 작업시간 × 살포시각) → REI + 안전 시각
  POST /explain  — 계산 결과에 대한 AI 안전 해석
  POST /chat     — 독립 '안전 도우미' Q&A (RAG, 미구성 시 폴백)
  GET  /suggested-questions — 추천 질문 리스트
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import explain, rei_lookup, rotation
from .rag import answer

app = FastAPI(title="Ieum Chatbot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용. 배포 시 웹 도메인으로 제한
    allow_methods=["*"],
    allow_headers=["*"],
)

SUGGESTED_QUESTIONS = [
    "재출입 제한시간이 뭐예요?",
    "장갑 끼면 더 빨리 들어가도 되나요?",
    "비가 오면 시간이 줄어드나요?",
    "헥시티아족스 다음엔 어떤 약을 쳐야 하나요?",
]


# ---------- schemas ----------
class ReiRequest(BaseModel):
    product: str                    # 농약 제품명 또는 유효성분명
    work_type: str                  # 예: "수확", "예찰"
    crop: str = "strawberry"
    work_hours: int | None = None   # 1/2/4/6/8. 미지정 시 보수적 기본값
    spray_time: str | None = None   # ISO. 있으면 안전 시각 계산


class ReiResponse(BaseModel):
    ingredient: str | None
    crop: str
    work_type: str
    work_hours_used: int | None
    rei_hours: float | None
    safe_time: str | None
    note: str
    explanation: str | None = None


class RotationRequest(BaseModel):
    pest: str | None = None           # 응애/진딧물/나방. 미지정 시 history로 추론
    history: list[str] = []           # 최근 사용 약제(오래된→최신)
    crop: str = "strawberry"


class ChatRequest(BaseModel):
    message: str
    crop: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


# ---------- endpoints ----------
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/suggested-questions")
def suggested_questions() -> dict[str, list[str]]:
    return {"questions": SUGGESTED_QUESTIONS}


@app.post("/rei", response_model=ReiResponse)
def rei(req: ReiRequest) -> ReiResponse:
    ingredient = rei_lookup.resolve_ingredient(req.product)
    if ingredient is None:
        return ReiResponse(
            ingredient=None, crop=req.crop, work_type=req.work_type,
            work_hours_used=req.work_hours, rei_hours=None, safe_time=None,
            note=f"'{req.product}'에 해당하는 농약/성분을 찾지 못했습니다.",
        )

    result = rei_lookup.lookup_rei(ingredient, req.work_type, req.work_hours, req.crop)

    safe_time = None
    spray_iso = rei_lookup.parse_spray_time(req.spray_time)  # ISO 또는 자연어 허용
    if result["rei_hours"] is not None and spray_iso:
        safe_time = rei_lookup.safe_reentry_time(spray_iso, result["rei_hours"])
    result["safe_time"] = safe_time

    explanation = explain.build_explanation(result) if result["rei_hours"] is not None else None

    return ReiResponse(**result, explanation=explanation)


@app.post("/explain")
def explain_result(result: dict) -> dict[str, str]:
    """이미 계산된 결과 dict를 받아 해석만 생성 (웹이 REI를 직접 계산한 경우)."""
    return {"explanation": explain.build_explanation(result)}


@app.post("/rotation")
def rotation_recommend(req: RotationRequest) -> dict:
    """방제 사이클(로테이션) 추천 — 같은 해충 타깃 & 다른 IRAC 그룹. 축소판."""
    result = rotation.recommend_rotation(req.pest, req.history, req.crop)
    result["explanation"] = rotation.build_rotation_explanation(result)
    return result


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # 1) 로테이션(다음에 뭘 칠지) 질문이면 추천 엔진으로 처리
    rot = rotation.try_answer_as_rotation(req.message)
    if rot is not None:
        return ChatResponse(answer=rot, sources=[])
    # 2) 그 외엔 RAG 안전 정보 Q&A
    result = answer(req.message, crop=req.crop)
    return ChatResponse(answer=result["answer"], sources=result.get("sources", []))
