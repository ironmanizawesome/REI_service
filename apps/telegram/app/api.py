from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.scheduler import list_jobs, schedule_alarm

router = APIRouter()


class ScheduleRequest(BaseModel):
    chat_id: str
    target_time: str
    message: str


@router.post("/api/schedule")
def schedule(req: ScheduleRequest):
    target_dt = datetime.fromisoformat(req.target_time)
    schedule_alarm(req.chat_id, target_dt, req.message)
    return {"success": True, "scheduled_time": req.target_time}


@router.get("/api/debug/jobs")
def get_scheduled_jobs():
    return {"jobs": list_jobs()}
