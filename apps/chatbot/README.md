# chatbot — 이음 RAG 챗봇 (규현)

딸기 농약 **로테이션 추천** + **REI 정보** Q&A. FastAPI + RAG.

## 실행

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env    # OPENAI_API_KEY 입력
uvicorn app.main:app --reload
```

- `GET /health` — 헬스체크
- `POST /chat` — `{"message": "...", "crop": "strawberry"}` → `{"answer", "sources"}`

RAG 인덱스 미구성 시 규칙 기반 폴백 응답이 나온다.

## 구조

```
app/
  main.py    # FastAPI, /chat 엔드포인트
  rag.py     # RAG 파이프라인 (build_index, answer) — 현재 스텁
knowledge/   # 인덱싱할 원본 문서
storage/     # 생성된 FAISS 인덱스 (gitignore)
```

## 할 일 (규현)

1. `knowledge/`에 REI 방법론·로테이션 규칙 문서 채우기
2. `rag.build_index()` 구현 — 로더 → 청킹 → 임베딩 → FAISS 저장
3. `rag._rag_answer()` 구현 — retriever + LLM 체인
4. 로테이션 추천 로직 — 작용기작 그룹 교차 규칙 + `../../data` 연동
