"""이음 챗봇 대화형 테스트 — 서버 없이 질문을 바꿔가며 /chat 을 눌러본다.

실행: cd apps/chatbot && python scripts/chat_repl.py

- 그냥 질문을 입력하면 안전 도우미(RAG) 답변 + 출처를 출력.
- `/rei` 입력 시 REI 룩업을 대화형으로 테스트.
- `:q` 또는 빈 줄 두 번으로 종료.
OPENAI_API_KEY 가 .env 에 있으면 실제 LLM, 없으면 폴백으로 동작한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/chatbot

from chatbot_app import llm, rei_lookup  # noqa: E402
from chatbot_app.explain import build_explanation  # noqa: E402
from chatbot_app.rag import answer  # noqa: E402


def rei_flow():
    print("  [REI 룩업] 성분/제품, 작업유형, 작업시간, 살포시각을 차례로 입력 (엔터=기본)")
    product = input("   농약/성분 (예: Bifenazate): ").strip() or "Bifenazate"
    work_type = input("   작업유형 (수확/예찰) [수확]: ").strip() or "수확"
    wh = input("   작업시간 (1/2/4/6/8, 엔터=보수적 기본): ").strip()
    work_hours = int(wh) if wh else None
    spray_raw = input("   살포시각 (ISO 또는 '5시간 전' 등, 엔터=생략): ").strip() or None
    spray = rei_lookup.parse_spray_time(spray_raw)
    if spray_raw and spray is None:
        print(f"   (살포시각 '{spray_raw}' 을(를) 해석 못 해 안전시각은 생략합니다)")

    ing = rei_lookup.resolve_ingredient(product)
    if ing is None:
        print(f"   → '{product}' 성분/제품을 찾지 못했습니다.\n")
        return
    if product.strip().lower() != ing.lower():
        print(f"   ('{product}' → {ing} 로 인식)")
    r = rei_lookup.lookup_rei(ing, work_type, work_hours)
    if r["rei_hours"] is not None and spray:
        r["safe_time"] = rei_lookup.safe_reentry_time(spray, r["rei_hours"])
    print(f"   → REI: {r['rei_hours']}시간 | 안전시각: {r.get('safe_time')} | {r['note'] or '-'}")
    if r["rei_hours"] is not None:
        print(f"   해석: {build_explanation(r)}")
    print()


def main():
    mode = "LLM 활성" if llm.llm_available() else "폴백(키 없음)"
    print(f"[이음 챗봇 REPL] 모드: {mode}")
    print("질문을 입력하세요. (/rei = REI 테스트, :q = 종료)\n")

    while True:
        try:
            q = input("나 > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q in (":q", "quit", "exit"):
            break
        if not q:
            continue
        if q == "/rei":
            rei_flow()
            continue

        res = answer(q)
        print(f"\n봇 > {res['answer']}")
        if res.get("sources"):
            print(f"    (출처: {', '.join(res['sources'])})")
        print()

    print("종료합니다.")


if __name__ == "__main__":
    main()
