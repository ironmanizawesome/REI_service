# chatbot — 이음 RAG 챗봇 (규현)

딸기 농약 **재출입(REI) 정보 + 안전 도우미 Q&A**. FastAPI 백엔드.
"숫자는 데이터에서 룩업, 설명만 LLM" 원칙 — 재출입 시간 환각 차단.

## 실행

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env    # OPENAI_API_KEY 입력(선택)
uvicorn chatbot_app.main:app --reload
```

`OPENAI_API_KEY`가 없으면 규칙 기반 폴백으로 동작하고, 넣으면 LLM 해석/답변으로 자동 전환됩니다(코드 수정 불필요).

## 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/suggested-questions` | 추천 질문 리스트 |
| POST | `/rei` | (농약/성분 × 작물 × 작업유형 × 작업시간 × 살포시각) → REI + 안전 시각 + AI 해석 |
| POST | `/explain` | 계산된 결과 dict → AI 안전 해석만 (웹이 REI를 직접 계산한 경우) |
| POST | `/rotation` | 방제 사이클 추천 — 같은 해충 타깃 & 다른 IRAC 그룹 (축소판) |
| POST | `/chat` | 독립 '안전 도우미' Q&A (RAG, 미구성 시 폴백) |

`/rei` 요청 예:

```json
{ "product": "Bifenazate", "crop": "strawberry",
  "work_type": "수확", "work_hours": 6, "spray_time": "2026-07-03T09:00:00" }
```

- `product`: 제품명 또는 유효성분명 (`data/products.json`·`active_ingredients.json` 기준)
- `work_hours` 미지정 시: 해당 작업유형의 가장 보수적(최대 REI) 값 사용
- REI 값 출처: `data/rei_results.json` (EFSA 2022 Guidance 팀 산정)

## RAG 인덱싱

```bash
# knowledge/*.md 를 임베딩해 storage/ 에 FAISS 인덱스 생성 (OPENAI_API_KEY 필요)
python -c "from chatbot_app.rag import build_index; print(build_index(), '청크 인덱싱')"
```

인덱스가 있으면 `/chat`이 검색+생성(RAG), 없고 키만 있으면 LLM 단독, 키도 없으면 폴백.

## 테스트

```bash
pip install pytest
pytest   # 키 없이 폴백 경로로 룩업·엔드포인트 검증
```

## 구조

```
chatbot_app/
  main.py        # FastAPI, 엔드포인트
  rei_lookup.py  # REI 룩업 + 안전 시각 계산
  explain.py     # AI 안전 해석 생성
  rag.py         # RAG 인덱싱/검색 (build_index, answer)
  llm.py         # LLM/임베딩 호출 격리 (교체 지점)
knowledge/       # RAG 원본 문서 (.md)
storage/         # FAISS 인덱스 (gitignore)
tests/           # 회귀 테스트
```

## 할 일 (규현)

1. 딸기 등록 제품 목록 → `data/products.json` (제품 검색용)
2. 작업시간/작업유형 최종 라벨을 프론트(은수)와 조율
3. IRAC 그룹·대상 해충 검증 (현재 `*_verified: false` 초안)
4. 방제 사이클 엔진 확장 (`DESIGN.md` §4) — 살포 주기·PHI·사용량 축, 대표 농약 리스트, FRAC(살균제)
5. 성분별 knowledge 문서 보강
