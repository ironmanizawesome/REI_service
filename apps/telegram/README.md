# apps/telegram

텔레그램 봇 + 재출입 알림 스케줄러. [apps/web](../web)과 분리된 독립 서비스로, 알림 예약/발송만 담당합니다.

## 실행 (포트 8100)

```
conda activate rei_service
python apps/telegram/run_server.py
```

## 환경변수

`apps/telegram/.env`:

```
TELEGRAM_BOT_TOKEN=...
```

[@BotFather](https://t.me/BotFather)에서 봇을 만들고 발급받은 토큰을 넣으세요. 토큰이 없으면 봇 polling은 비활성화된 채로 서버만 뜹니다(로그에 안내 출력).

## Chat ID 확보 (수동 방식)

1. 텔레그램에서 봇 검색 → `/start` 전송
2. 봇이 답장하는 숫자가 Chat ID — 이 값을 [apps/web](../web) 화면의 "텔레그램 Chat ID" 입력창에 사용

## API

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/schedule` | 알림 예약 (내부용, `apps/web`이 호출). Body: `chat_id`, `target_time`(ISO 8601), `message` |
| GET | `/api/debug/jobs` | 현재 예약된 job 목록 확인용 디버그 엔드포인트 |

## 참고

- 예약된 알림은 메모리(APScheduler `BackgroundScheduler`)에만 저장됩니다 — 서버를 재시작하면 사라집니다(프로토타입 단계).
- 텔레그램 polling(`Application.updater.start_polling()`)과 스케줄러는 서로 다른 실행 모델(asyncio 이벤트 루프 vs 별도 스레드)로 동작해 서로를 막지 않습니다.
