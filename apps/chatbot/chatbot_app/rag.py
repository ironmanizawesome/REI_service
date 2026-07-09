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


def _load_documents() -> list:
    """knowledge/*.md 를 langchain Document로 로드 (README 제외)."""
    from langchain_core.documents import Document

    docs = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def build_index() -> int:
    """knowledge/ 문서를 임베딩해 벡터스토어(FAISS)로 저장.

    로더 → 청킹 → 임베딩(llm.get_embeddings) → FAISS.save_local(STORAGE_DIR)
    return: 인덱싱된 청크 수. OPENAI_API_KEY 필요.
    """
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from . import llm

    docs = _load_documents()
    if not docs:
        raise RuntimeError(f"knowledge 문서가 없습니다: {KNOWLEDGE_DIR}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    store = FAISS.from_documents(chunks, llm.get_embeddings())
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(STORAGE_DIR))
    return len(chunks)


def _rag_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and (STORAGE_DIR / "index.faiss").exists()


def answer(message: str, crop: str | None = None) -> dict:
    """질의에 대한 답변 반환.

    우선순위: RAG(인덱스+키) → LLM 단독(키만) → 규칙 폴백.
    """
    from . import llm

    if _rag_available():
        # TODO(규현): FAISS 로드 → retriever → LLM 체인으로 교체
        return _rag_answer(message, crop)
    if llm.llm_available():
        return _llm_only_answer(message, crop)
    return _fallback_answer(message, crop)


_RAG_SYSTEM = (
    "너는 한국 시설재배 농가를 돕는 농약 안전 도우미다. "
    "아래 '참고 자료'에 있는 내용만 근거로 쉽고 정확한 한국어로 답한다. "
    "참고 자료에 없는 내용은 추측하지 말고 '자료에 없어 확실치 않다'고 밝히고 "
    "라벨·전문기관 확인을 권한다. 구체 수치를 지어내지 않는다."
)


def _rag_answer(message: str, crop: str | None) -> dict:
    """FAISS 검색 → 관련 청크를 근거로 LLM 생성. 출처 파일명 반환."""
    from langchain_community.vectorstores import FAISS

    from . import llm

    store = FAISS.load_local(
        str(STORAGE_DIR), llm.get_embeddings(), allow_dangerous_deserialization=True
    )
    docs = store.similarity_search(message, k=4)
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    sources = list(dict.fromkeys(d.metadata.get("source", "?") for d in docs))

    hint = f"\n(작물: {crop})" if crop else ""
    user = f"참고 자료:\n{context}\n\n질문: {message}{hint}"
    try:
        text = llm.generate(_RAG_SYSTEM, user)
    except Exception:
        return _fallback_answer(message, crop)
    return {"answer": text, "sources": sources}


def _llm_only_answer(message: str, crop: str | None) -> dict:
    """인덱스 없이 LLM만으로 답변 (RAG 구성 전 임시). 출처는 비움."""
    from . import llm

    system = (
        "너는 한국 시설재배 농가를 돕는 농약 안전 도우미다. "
        "재출입 안전, 보호장비, 농약 사용 주의사항을 쉽고 정확한 한국어로 답한다. "
        "확실하지 않으면 단정하지 말고, 구체 수치는 라벨·전문기관 확인을 권한다."
    )
    hint = f" (작물: {crop})" if crop else ""
    try:
        text = llm.generate(system, message + hint)
        return {"answer": text, "sources": []}
    except Exception:
        return _fallback_answer(message, crop)


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
