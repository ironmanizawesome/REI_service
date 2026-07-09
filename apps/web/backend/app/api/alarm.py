import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

TELEGRAM_SERVICE_URL = os.getenv("TELEGRAM_SERVICE_URL", "http://localhost:8100")


class AlarmRequest(BaseModel):
    chat_id: str
    target_time: str
    compound: str
    crop: str


@router.post("/api/alarm")
def create_alarm(req: AlarmRequest):
    message = (
        f"🌱 안심 재출입 알림\n"
        f"{req.compound} 살포 {req.crop}, 지금부터 안전하게 재출입하실 수 있어요!"
    )
    try:
        resp = httpx.post(
            f"{TELEGRAM_SERVICE_URL}/api/schedule",
            json={"chat_id": req.chat_id, "target_time": req.target_time, "message": message},
            timeout=5.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"텔레그램 서비스 호출에 실패했습니다: {e}")
    return {"success": True, "scheduled_time": req.target_time}
