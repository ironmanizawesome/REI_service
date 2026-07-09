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
REI = (DT50 / ln2) × ln( TC×H×DFR₀×MAF×max(DAFproduct,DAFdilution) / (1000×BW×AOEL) )
```

## 계산 방식

최종 REI 값은 **EFSA 2022 Guidance 기준으로 직접 산정**하며, 작업유형(수확/예찰)·작업시간(1·2·4·6·8h)별 값을 `data/rei_results.json` 룩업 테이블에서 제공한다.

`packages/rei_core`의 Method A(박연기 2021 폐쇄형 로그식)·Method B(EPA 기본 REI × DT50 보정)는 **최종 산정에는 쓰지 않으며, 시도·비교용 참고 코드로만 유지**한다.

## 모노레포 구조

```
REI_service/
├── apps/
│   └── chatbot/      # RAG 챗봇 (규현) — 딸기 농약 로테이션/REI 정보. FastAPI
│       #  web/       # (은수 담당 — 별도 세팅)
│       #  telegram/  # (채윤·은수 담당 — 별도 세팅)
├── packages/
│   └── rei_core/     # 공용 REI 계산 로직 (참고용 Method A/B)
├── data/             # 공용 데이터 (REI 룩업 + 성분/DT50 스키마)
└── README.md
```

## 담당

| 파트 | 담당 | 스택 |
|------|------|------|
| RAG 챗봇 | 규현 | Python / FastAPI / (LangChain 등) |
| 웹 | 은수 | (미정) |
| 텔레그램 봇 | 은수·채윤 | (미정) |
| REI 계산·데이터 | 공용 | Python (`packages/rei_core`, `data/`) |

## 빠른 시작

```bash
# 챗봇 (규현)
cd apps/chatbot && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload
```

웹(은수)·텔레그램 봇(채윤·은수)은 각 담당자가 `apps/web`, `apps/telegram`에 별도 세팅.
