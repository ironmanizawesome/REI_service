# 이음 — REI 재출입 안전 자문 서비스

시설재배 농약 **재출입 안전 자문 서비스**. 한국은 소비자 안전을 위한 PHI(수확 전 안전사용기간) 기준은 있으나 작업자 재출입 기준(REI)이 없어, EPA WPS·EFSA Guidance를 참조 프레임으로 안전 재출입 시점을 산정한다.

전북대 IX-PBL 여름 프로젝트 · 팀 **이음** (3인).

**최종 목표: 웹 배포** — 실제 접속 가능한 서비스로 공개하는 것을 목표로 한다.

## 대상 범위

- 작물: 딸기
- 활성성분: 살충·살비제 6종 — Hexythiazox, Fenpyroximate, Spirodiclofen, Bifenazate, Acetamiprid, Chlorantraniliprole (계수 확보 성분 기준 선정)
- 살균제(FRAC)는 추후 검토 대상 (`apps/chatbot/DESIGN.md` 참고)

## 핵심 수식

```
(은수 수식 기입 예정)
```

## 계산 방식

최종 REI 값은 **EFSA 2022 Guidance 계산식(`apps/web/backend/app/calculator.py`)으로 직접 계산**해 제공한다. 성분 × 작업유형(수확/예찰) × 작업시간 × 보호장비(없음/작업복/작업복+장갑) 전 조합을 실시간 산출하므로 누락 조합이 없다. `data/rei_results.json`은 '없음' 기준값 스냅샷으로, calculator 산출값과 일치함을 검증한 **참고·검증용**으로만 유지한다.

`packages/rei_core`의 Method A(박연기 2021 폐쇄형 로그식)·Method B(EPA 기본 REI × DT50 보정)는 **최종 산정에는 쓰지 않으며, 시도·비교용 참고 코드로만 유지**한다.

## 모노레포 구조

```
REI_service/
├── apps/
│   ├── chatbot/      # AI 백엔드 (규현) — chatbot_app: REI 룩업·AI 해석·RAG·로테이션. FastAPI
│   ├── web/          # 웹 (은수) — frontend(React) + backend(REI표·알림 + 챗봇 /ai 마운트)
│   └── telegram/     # 텔레그램 알림 워커 (채윤·은수) — 봇 폴링 + 스케줄러
├── packages/
│   └── rei_core/     # 공용 REI 계산 로직 (참고용 Method A/B)
├── data/             # 공용 데이터 (REI 룩업 + 성분/DT50 스키마)
└── README.md
```

**통합 구조:** 웹 백엔드(`apps/web/backend`)가 프론트가 보는 **단일 백엔드**이며, 챗봇 AI(`chatbot_app`)를 `/ai` 로 서브앱 마운트한다. 텔레그램은 성격이 다른 별도 알림 워커로, 웹 백엔드가 `/api/alarm` → 텔레그램 `/api/schedule` HTTP로 연동한다.

## 담당

| 파트 | 담당 | 스택 |
|------|------|------|
| RAG 챗봇 | 규현 | Python / FastAPI / (LangChain 등) |
| 웹 | 은수 | (미정) |
| 텔레그램 봇 | 은수·채윤 | (미정) |
| REI 계산·데이터 | 공용 | Python (`packages/rei_core`, `data/`) |

## 빠른 시작 (통합 실행)

**1) 웹 백엔드 (= 단일 백엔드, 챗봇 `/ai` 포함) — 포트 8000**

```bash
cd apps/web/backend
pip install -r requirements.txt                    # 웹 + 챗봇 의존성
# 챗봇 AI 사용 시: apps/chatbot/.env 에 OPENAI_API_KEY, RAG 인덱스 1회 생성
python -c "import sys; sys.path.insert(0,'../../chatbot'); from chatbot_app.rag import build_index; print(build_index(),'청크')"
python run_server.py                               # http://127.0.0.1:8000
```

**2) 프론트 — 포트 5173**

```bash
cd apps/web/frontend && npm install && npm run dev  # VITE_API_BASE_URL 기본 :8000
```

**3) 텔레그램 알림 워커 (별도) — 포트 8100**

```bash
cd apps/telegram && pip install -r requirements.txt
# .env 에 TELEGRAM_BOT_TOKEN
python run_server.py
```

챗봇만 독립 실행하려면: `cd apps/chatbot && uvicorn chatbot_app.main:app --reload`
