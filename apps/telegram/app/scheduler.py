from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.telegram_bot import send_message_sync

_scheduler = BackgroundScheduler()
_scheduler.start()


def schedule_alarm(chat_id: str, target_datetime: datetime, message: str) -> None:
    _scheduler.add_job(
        send_message_sync,
        "date",
        run_date=target_datetime,
        args=[chat_id, message],
        misfire_grace_time=None,  # 살짝 늦게 실행되더라도 건너뛰지 않고 항상 발송
    )


def list_jobs() -> list[dict]:
    jobs = []
    for job in _scheduler.get_jobs():
        chat_id, message = job.args
        jobs.append({
            "id": job.id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "chat_id": chat_id,
            "message": message,
        })
    return jobs
