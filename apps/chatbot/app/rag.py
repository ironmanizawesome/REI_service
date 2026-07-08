"""RAG 파이프라인 뼈대 (규현).

목표:
1. knowledge/ 문서(REI 방법론, 농약 로테이션 규칙, 제품 라벨)를 인덱싱
2. 질의 시 관련 청크 검색 → LLM으로 답변 생성
3. 딸기 농약 로테이션은 작용기작(FRAC/IRAC) 그룹 교차 규칙 기반 추천

현재는 스텁: 벡터스토어/LLM 미구성 시 규칙 기반 폴백을 반환한다.
build_index() 를 채우고 answer() 의 RAG 경로를 연결하면 된다.
"""

from __future__ import annotations

import os
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"


def build_index() -> None:
    """knowledge/ 문서를 임베딩해 벡터스토어(FAISS)로 저장.

    TODO(규현):
      - langchain 문서 로더로 knowledge/*.md 로드
      - text splitter로 청크 분할
      - OpenAI 임베딩 → FAISS.save_local(STORAGE_DIR)
    """
    raise NotImplementedError("build_index: RAG 인덱싱 미구현 (스텁)")


def _rag_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and (STORAGE_DIR / "index.faiss").exists()


def answer(message: str, crop: str | None = None) -> dict:
    """질의에 대한 답변 반환.

    RAG 구성 시 검색+생성, 미구성 시 규칙 기반 폴백.
    """
    if _rag_available():
        # TODO(규현): FAISS 로드 → retriever → LLM 체인으로 교체
        return _rag_answer(message, crop)
    return _fallback_answer(message, crop)


def _rag_answer(message: str, crop: str | None) -> dict:
    raise NotImplementedError("_rag_answer: RAG 검색/생성 미구현 (스텁)")


def _fallback_answer(message: str, crop: str | None) -> dict:
    """RAG 미구성 시 임시 응답. 데모/개발용."""
    hint = f"(작물: {crop}) " if crop else ""
    return {
        "answer": (
            f"{hint}이음 챗봇 뼈대입니다. RAG 인덱스가 아직 구성되지 않았습니다.\n"
            "knowledge/ 에 문서를 넣고 build_index() 를 실행한 뒤 OPENAI_API_KEY 를 "
            "설정하면 딸기 농약 로테이션·REI 정보 답변이 활성화됩니다."
        ),
        "sources": [],
    }
