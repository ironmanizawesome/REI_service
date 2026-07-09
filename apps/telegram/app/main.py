from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.telegram_bot import start_bot_polling, stop_bot_polling


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_bot_polling()
    yield
    await stop_bot_polling()


app = FastAPI(title="REI Telegram Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
