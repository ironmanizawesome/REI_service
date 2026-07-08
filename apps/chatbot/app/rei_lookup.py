"""REI 룩업 + 안전 재출입 시각 계산 (규현).

최종 REI 값은 계산이 아니라 data/rei_results.json 룩업에서 온다
(EFSA 2022 Guidance 기준 팀 산정값). 이 모듈은:
  1. 제품명 → 유효성분 매핑 (products.json)
  2. (성분 × 작물 × 작업유형 × 작업시간) → REI 시간 룩업
  3. 살포 시각 + REI → 안전 재출입 시각 산출

작업시간 미지정 시: 해당 작업유형에서 산정된 값 중 가장 보수적(최대 REI)을
기본값으로 사용한다. ⚠️ 프론트 확정 흐름과 작업시간 처리 방식은 은수와 조율 필요.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _load(name: str) -> dict:
    return json.loads((_DATA_DIR / name).read_text(encoding="utf-8"))


def resolve_ingredient(query: str) -> str | None:
    """제품명 또는 성분명 → 표준 유효성분명(name_en). 못 찾으면 None."""
    q = query.strip().lower()

    # 1) 유효성분 직접 일치
    ai = _load("active_ingredients.json").get("active_ingredients", [])
    for row in ai:
        if q in (row.get("name_en", "").lower(), row.get("name_ko", "").lower()):
            return row["name_en"]

    # 2) 제품명 → 성분 매핑
    for p in _load("products.json").get("products", []):
        if q == p.get("product_name", "").lower():
            return p.get("active_ingredient")

    return None


def lookup_rei(
    ingredient: str,
    work_type: str,
    work_hours: int | None = None,
    crop: str = "strawberry",
) -> dict:
    """(성분 × 작물 × 작업유형 × 작업시간) → REI 시간.

    return: { ingredient, crop, work_type, work_hours_used, rei_hours, note }
    값 없으면 rei_hours=None, note에 사유.
    """
    results = _load("rei_results.json").get("results", [])
    row = next((r for r in results if r["active_ingredient"].lower() == ingredient.lower()), None)
    if row is None:
        return _miss(ingredient, crop, work_type, work_hours, "성분 데이터 없음")

    table = row.get("by_work_type", {}).get(work_type)
    if not table:
        return _miss(ingredient, crop, work_type, work_hours,
                     f"작업유형 '{work_type}' 데이터 없음 (가능: {list(row['by_work_type'])})")

    if work_hours is not None:
        val = table.get(str(work_hours))
        if val is None:
            return _miss(ingredient, crop, work_type, work_hours,
                         f"작업시간 {work_hours}h 데이터 없음 (가능: {list(table)})")
        hours_used, note = work_hours, ""
    else:
        # 보수적 기본값: 최대 REI가 나오는 작업시간
        hours_used = max(table, key=lambda h: table[h] or 0)
        val = table[hours_used]
        hours_used = int(hours_used)
        note = "작업시간 미지정 → 가장 보수적(최대 REI) 값 사용"

    return {
        "ingredient": ingredient,
        "crop": crop,
        "work_type": work_type,
        "work_hours_used": hours_used,
        "rei_hours": val,
        "note": note,
    }


def _miss(ingredient, crop, work_type, work_hours, why) -> dict:
    return {
        "ingredient": ingredient, "crop": crop, "work_type": work_type,
        "work_hours_used": work_hours, "rei_hours": None, "note": why,
    }


def safe_reentry_time(spray_time_iso: str, rei_hours: float) -> str:
    """살포 시각(ISO) + REI 시간 → 안전 재출입 시각(ISO)."""
    spray = datetime.fromisoformat(spray_time_iso)
    return (spray + timedelta(hours=rei_hours)).isoformat()
