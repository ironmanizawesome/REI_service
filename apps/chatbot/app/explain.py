"""AI 안전 해석 생성 (규현) — 목업 '결과 화면 AI 해석' 대응.

원칙: REI 시간·안전 시각 등 숫자는 입력값(룩업 결과)을 그대로 쓰고,
LLM은 그것을 농민 친화적으로 '설명'만 한다. 숫자를 새로 지어내지 않음.

키 없으면 규칙 기반 폴백 템플릿으로 동일 정보 제공.
"""

from __future__ import annotations

from . import llm

_SYSTEM = (
    "너는 한국 시설재배 농가를 돕는 농약 재출입 안전 도우미다. "
    "농민이 이해하기 쉬운 짧고 따뜻한 한국어로 설명한다. "
    "제공된 숫자(재출입 제한시간, 안전 시각)는 절대 바꾸지 말고 그대로 인용한다. "
    "규제나 위반을 강조하지 말고, 부득이 더 일찍 들어가야 하면 긴소매·장갑·마스크 등 "
    "보호장비 착용을 권한다. 없는 수치를 지어내지 않는다."
)


def build_explanation(result: dict) -> str:
    """룩업 결과(dict)를 받아 해석 텍스트 생성.

    기대 키: ingredient, crop, work_type, rei_hours, safe_time(optional), work_hours_used
    """
    facts = _facts_block(result)

    if llm.llm_available():
        try:
            user = (
                f"다음 계산 결과를 농민에게 설명해줘.\n{facts}\n"
                "2~4문장으로. 재출입 제한시간과 안전 시각을 그대로 언급하고, "
                "이른 재출입 시 보호장비 안내를 덧붙여."
            )
            return llm.generate(_SYSTEM, user)
        except Exception:
            pass  # 실패 시 폴백

    return _fallback(result)


def _facts_block(r: dict) -> str:
    lines = [
        f"- 유효성분: {r.get('ingredient')}",
        f"- 작물: {r.get('crop')}",
        f"- 작업유형: {r.get('work_type')}",
        f"- 재출입 제한시간: {r.get('rei_hours')}시간",
    ]
    if r.get("work_hours_used") is not None:
        lines.append(f"- 기준 작업시간: {r.get('work_hours_used')}시간")
    if r.get("safe_time"):
        lines.append(f"- 안전 재출입 시각: {r.get('safe_time')}")
    return "\n".join(lines)


def _fallback(r: dict) -> str:
    rei = r.get("rei_hours")
    ing = r.get("ingredient")
    safe = r.get("safe_time")
    if rei == 0:
        return (
            f"{ing} 살포 후 이 작업({r.get('work_type')})은 별도의 대기 없이 "
            "들어가셔도 되는 것으로 나왔습니다. 그래도 살포 직후에는 환기를 하고, "
            "피부에 잔류물이 닿지 않도록 긴소매·장갑 착용을 권합니다."
        )
    when = f" 안전 재출입 시각은 {safe} 입니다." if safe else ""
    return (
        f"{ing} 살포 후 이 작업({r.get('work_type')})은 약 {rei}시간 뒤에 "
        f"들어가시는 것이 안전합니다.{when} "
        "부득이 더 일찍 들어가야 한다면 긴소매·장갑·마스크 등 보호장비를 꼭 착용하세요."
    )
