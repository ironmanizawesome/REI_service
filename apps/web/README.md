# apps/web

재출입 제한시간(REI) 계산기 — 사용자가 직접 쓰는 웹 화면과 그 API.

## 구성

```
web/
├── backend/   # FastAPI: REI 계산표 조회, 알림 설정 요청 처리
└── frontend/  # Vite + React: 계산기 화면
```

## 실행

### backend (포트 8000)

```
conda activate rei_service
python apps/web/backend/run_server.py
```

### frontend (포트 5173)

```
cd apps/web/frontend
npm install
npm run dev
```

## 환경변수

- `apps/web/frontend/.env` → `VITE_API_BASE_URL` (기본 `http://localhost:8000`)
- `TELEGRAM_SERVICE_URL` (backend, 선택) → [apps/telegram](../telegram) 서비스 주소, 기본 `http://localhost:8100`

## API

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/rei-table` | 성분/작업유형/작업시간/보호장비별 REI 계산표 |
| GET | `/api/compound-products` | 성분 → 농약 상품명 매핑 |
| POST | `/api/alarm` | 재출입 알림 예약 요청 (내부적으로 [apps/telegram](../telegram)의 `/api/schedule`을 호출) |

`POST /api/alarm`이 동작하려면 `apps/telegram` 서비스가 먼저 떠 있어야 합니다.
