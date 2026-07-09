"""방제 사이클(로테이션) 추천 엔진 — 축소판 (규현).

DESIGN.md §4의 다축 엔진 중 '저항성 로테이션' 축을 6종 데이터로 먼저 구현.
원칙: 같은 대상 해충끼리만 로테이션하고, 그 안에서 IRAC 그룹을 교차시켜
저항성 발달을 늦춘다. 결정론적 규칙으로 후보를 산출하고, LLM은 설명만 한다.

⚠️ irac_group·target_pest 는 초안(미검증). 아직 다루지 않는 축:
   살포 주기, PHI·최대 사용횟수, 희석/사용량, 실제 농가 사용이력.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import llm, rei_lookup

_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _ingredients() -> list[dict]:
    data = json.loads((_DATA_DIR / "active_ingredients.json").read_text(encoding="utf-8"))
    return data.get("active_ingredients", [])


def _row_for(name: str) -> dict | None:
    """입력(제품/성분/한글/별칭)을 표준 성분 row로. 관대한 매칭 재사용."""
    en = rei_lookup.resolve_ingredient(name)
    if not en:
        return None
    return next((r for r in _ingredients() if r.get("name_en") == en), None)


def recommend_rotation(
    pest: str | None = None,
    history: list[str] | None = None,
    crop: str = "strawberry",
) -> dict:
    """다음 살포 후보 추천.

    pest: 대상 해충(응애/진딧물/나방). 미지정 시 history 마지막 약제에서 추론.
    history: 최근 사용 약제(오래된→최신). 마지막이 직전 사용.
    """
    history = history or []
    hist_rows = [r for r in (_row_for(h) for h in history) if r]

    if pest is None and hist_rows:
        pest = hist_rows[-1].get("target_pest")
    if pest is None:
        return {
            "target_pest": None, "used_irac_groups": [], "recommendations": [],
            "note": "대상 해충을 알 수 없습니다. 해충을 지정하거나 직전 사용 약제를 알려주세요.",
            "unverified": True,
        }

    used_groups = {r.get("irac_group") for r in hist_rows}
    used_names = {r.get("name_en") for r in hist_rows}

    candidates = [
        r for r in _ingredients()
        if r.get("target_pest") == pest and r.get("name_en") not in used_names
    ]

    recs = []
    for r in candidates:
        diff = r.get("irac_group") not in used_groups
        recs.append({
            "ingredient": r["name_en"],
            "name_ko": r.get("name_ko"),
            "irac_group": r.get("irac_group"),
            "class": r.get("class"),
            "recommended": diff,
            "reason": ("직전 사용과 다른 IRAC 그룹 — 저항성 관리에 적합"
                       if diff else "직전 사용과 같은 IRAC 그룹 — 로테이션 효과 낮음"),
        })
    recs.sort(key=lambda x: (not x["recommended"], x["irac_group"] or ""))

    note = ""
    if not candidates:
        note = "같은 해충 타깃의 다른 약제가 데이터에 없습니다 (로테이션 대상 부족)."
    elif not any(x["recommended"] for x in recs):
        note = "후보가 모두 직전 사용과 같은 IRAC 그룹입니다."

    return {
        "target_pest": pest,
        "used_irac_groups": sorted(g for g in used_groups if g),
        "recommendations": recs,
        "note": note,
        "unverified": True,  # irac_group·target_pest 초안임을 표시
    }


_SYSTEM = (
    "너는 한국 딸기 농가를 돕는 농약 방제 안내자다. "
    "제공된 추천 목록(성분·IRAC 그룹)만 근거로, 왜 이렇게 번갈아 쓰는지(저항성 관리) "
    "쉬운 한국어로 2~3문장 설명한다. 목록에 없는 약제를 지어내지 않는다. "
    "이 추천은 저항성 로테이션만 고려한 초안이며 살포 주기·안전사용기간은 별도 확인이 "
    "필요함을 한 줄 덧붙인다."
)


def build_rotation_explanation(result: dict) -> str | None:
    """추천 결과를 농민 친화적으로 설명. 키 없으면 폴백 템플릿."""
    recs = [r for r in result.get("recommendations", []) if r["recommended"]]
    if not recs:
        return None

    if llm.llm_available():
        try:
            listed = ", ".join(f"{r['name_ko']}(IRAC {r['irac_group']})" for r in recs)
            user = f"대상 해충: {result['target_pest']}\n추천 약제: {listed}\n이걸 설명해줘."
            return llm.generate(_SYSTEM, user)
        except Exception:
            pass

    names = ", ".join(f"{r['name_ko']}(IRAC {r['irac_group']})" for r in recs)
    return (
        f"{result['target_pest']} 방제는 같은 계열 약을 연속으로 쓰면 내성이 생기기 쉽습니다. "
        f"직전과 다른 IRAC 그룹인 {names} 중에서 번갈아 쓰시면 저항성 관리에 도움이 됩니다. "
        "다만 이 추천은 저항성 로테이션만 본 것이라, 살포 주기·수확 전 안전사용기간은 라벨에서 함께 확인하세요."
    )
