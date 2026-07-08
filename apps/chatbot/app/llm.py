"""LLM / 임베딩 호출 격리 지점 (규현).

생성·임베딩 호출을 여기 한 곳에 모아, 나중에 공급자 교체를 쉽게 한다.
- 1차: OpenAI 통일 (생성 + 임베딩)
- 후속: 임베딩만 bge-m3(한국어) 등으로 교체 → get_embeddings() 내부만 수정

OPENAI_API_KEY 미설정 시 llm_available()=False → 각 기능은 폴백 경로 사용.
"""

from __future__ import annotations

import os

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.4")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")


def llm_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _client():
    from openai import OpenAI  # 지연 임포트 — 미설치·미사용 시 부담 없음

    return OpenAI()


def generate(system: str, user: str, temperature: float = 0.3) -> str:
    """시스템+사용자 프롬프트로 텍스트 생성. 키 없으면 RuntimeError.

    호출부는 llm_available()로 먼저 확인하고, 미가용 시 폴백을 쓸 것.
    """
    if not llm_available():
        raise RuntimeError("OPENAI_API_KEY 미설정 — generate() 호출 불가")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    client = _client()
    try:
        resp = client.chat.completions.create(
            model=CHAT_MODEL, temperature=temperature, messages=messages
        )
    except Exception as e:
        # 일부 GPT-5 계열은 기본(1) 외 temperature 를 거부 → 파라미터 없이 재시도
        if "temperature" in str(e).lower():
            resp = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
        else:
            raise
    return resp.choices[0].message.content.strip()


def get_embeddings():
    """RAG 인덱싱/검색용 임베딩 객체 반환. ← 교체 지점.

    현재: OpenAI 임베딩. 한국어 검색 품질이 아쉬우면 이 함수 내부만
    HuggingFace bge-m3 등으로 바꾸면 되고, 이후 인덱스 재생성 필요.
    """
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=EMBED_MODEL)
