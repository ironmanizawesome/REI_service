import asyncio
import os

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

_application: Application | None = None


async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"안녕하세요! 당신의 Chat ID는 {chat_id} 입니다. 이 번호를 재출입 알림 설정 화면에 입력해주세요."
    )


async def start_bot_polling() -> None:
    global _application
    if not BOT_TOKEN:
        print("[telegram_bot] TELEGRAM_BOT_TOKEN이 설정되지 않아 봇 polling을 시작하지 않습니다.")
        return

    _application = Application.builder().token(BOT_TOKEN).build()
    _application.add_handler(CommandHandler("start", _start_command))

    await _application.initialize()
    await _application.start()
    await _application.updater.start_polling()


async def stop_bot_polling() -> None:
    global _application
    if not _application:
        return
    await _application.updater.stop()
    await _application.stop()
    await _application.shutdown()
    _application = None


def send_message_sync(chat_id: str, message: str) -> None:
    """APScheduler는 별도 스레드에서 job을 실행하므로 그 안에서 새 이벤트 루프로 메시지를 보낸다."""
    if not BOT_TOKEN:
        print("[telegram_bot] TELEGRAM_BOT_TOKEN이 설정되지 않아 메시지를 보낼 수 없습니다.")
        return
    bot = Bot(token=BOT_TOKEN)
    asyncio.run(bot.send_message(chat_id=chat_id, text=message))
