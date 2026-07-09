from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.alarm import router as alarm_router
from app.api.rei import router as rei_router

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
