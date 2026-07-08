"""이음 챗봇 패키지.

패키지 임포트 시 .env 를 로드해, uvicorn 실행이든 `python -c ...`(build_index)든
어느 경로로 진입해도 OPENAI_API_KEY 등 환경변수가 적용되게 한다.
탐색 순서: apps/chatbot/.env → 저장소 루트 .env.
"""

from pathlib import Path

try:
    from dotenv import load_dotenv

    _here = Path(__file__).resolve().parent          # apps/chatbot/app
    for _candidate in (_here.parent / ".env", _here.parents[2] / ".env"):
        if _candidate.exists():
            load_dotenv(_candidate)
except ImportError:
    pass  # python-dotenv 미설치 시에도 임포트는 되게 (환경변수 직접 설정 가정)
