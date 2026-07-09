import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.alarm import router as alarm_router
from app.api.rei import router as rei_router

# 챗봇(AI) 백엔드를 서브앱으로 마운트해 단일 서비스로 통합.
# chatbot_app 패키지는 apps/chatbot 아래에 있으므로 import 경로 추가.
_CHATBOT_DIR = Path(__file__).resolve().parents[4] / "apps" / "chatbot"
if str(_CHATBOT_DIR) not in sys.path:
    sys.path.insert(0, str(_CHATBOT_DIR))
from chatbot_app.main import app as chatbot_ai_app  # noqa: E402

app = FastAPI(title="REI Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rei_router)
app.include_router(alarm_router)

# 챗봇 AI 엔드포인트: /ai/chat, /ai/explain, /ai/rei, /ai/rotation ...
app.mount("/ai", chatbot_ai_app)
