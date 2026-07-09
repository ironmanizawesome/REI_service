"""이음 챗봇 스모크 테스트 — 서버 없이 엔드포인트를 한 번에 눌러 결과 출력.

실행: cd apps/chatbot && python scripts/smoke_test.py

OPENAI_API_KEY 가 .env 에 있으면 LLM 경로, 없으면 폴백 경로로 돈다.
어느 쪽이든 /rei 숫자·안전시각은 동일하게 나오고, explanation·/chat 문장만 달라진다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/chatbot

from fastapi.testclient import TestClient  # noqa: E402

from chatbot_app import llm  # noqa: E402
from chatbot_app.main import app  # noqa: E402

client = TestClient(app)


def show(title, obj):
    print(f"\n=== {title} ===")
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"  {k}: {v}")
    else:
        print(" ", obj)


def main():
    mode = "LLM 활성" if llm.llm_available() else "폴백(키 없음)"
    print(f"[모드] {mode}")

    show("GET /health", client.get("/health").json())
    show("GET /suggested-questions", client.get("/suggested-questions").json())

    rei = client.post("/rei", json={
        "product": "Bifenazate", "crop": "strawberry",
        "work_type": "수확", "work_hours": 6, "spray_time": "2026-07-03T09:00:00",
    }).json()
    show("POST /rei (Bifenazate 수확 6h)", rei)

    chat = client.post("/chat", json={
        "message": "비가 오면 재출입 시간이 줄어드나요?",
    }).json()
    show("POST /chat", chat)

    print("\n[확인 포인트]")
    print("  - /rei rei_hours=101.8, safe_time=2026-07-07T14:48:00 (키 유무와 무관)")
    print("  - 키 넣으면 explanation·/chat 이 LLM 문장으로 바뀌고, RAG면 sources 채워짐")


if __name__ == "__main__":
    main()
