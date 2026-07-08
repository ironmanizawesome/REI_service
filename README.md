# 그린타임 (GreenTime) — REI Service

시설재배 농약 **재출입 안전 자문 서비스**. 한국은 소비자 안전을 위한 PHI(수확 전 안전사용기간) 기준은 있으나 작업자 재출입 기준(REI)이 없어, EPA WPS를 참조 프레임으로 안전 재출입 시점을 산정한다.

전북대 IX-PBL 여름 프로젝트 (3인 팀).

## 대상 범위

- 활성성분: azoxystrobin, abamectin, boscalid (대표 3종)
- 작물: 딸기, 오이, 토마토
- 등록 제품 14종 (활성성분 13종)

## 핵심 수식

```
REI = (1/k) · ln[(DFR₀ · TC · H) / (BW · AOEL)]     (MOE ≥ 100)
```

현재 계산 방식: **Method B** (EPA 기본 REI × DT50 감쇠 보정). DAF 변동성으로 인한 Method A 불안정성을 우회.

## 모노레포 구조

```
REI_service/
├── apps/
│   └── chatbot/      # RAG 챗봇 (규현) — 딸기 농약 로테이션/REI 정보. FastAPI
│       #  web/       # (은수 담당 — 별도 세팅)
│       #  telegram/  # (채윤·은수 담당 — 별도 세팅)
├── packages/
│   └── rei_core/     # 공용 REI 계산 로직 (Method B)
├── data/             # 공용 데이터 (REI/DFR/DT50/AOEL 스키마 + 샘플)
└── README.md
```

## 담당

| 파트 | 담당 | 스택 |
|------|------|------|
| RAG 챗봇 | 규현 | Python / FastAPI / (LangChain 등) |
| 웹 | 은수 | Vite + React |
| 텔레그램 봇 | 은수·채윤 | python-telegram-bot |
| REI 계산·데이터 | 공용 | Python (`packages/rei_core`, `data/`) |

## 빠른 시작

```bash
# 챗봇 (규현)
cd apps/chatbot && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload
```

웹(은수)·텔레그램 봇(채윤·은수)은 각 담당자가 `apps/web`, `apps/telegram`에 별도 세팅.
