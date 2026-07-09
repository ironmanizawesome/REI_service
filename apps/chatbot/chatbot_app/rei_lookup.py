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

import difflib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _load(name: str) -> dict:
    return json.loads((_DATA_DIR / name).read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    """공백 제거 + 소문자. 한글 표기 변형 매칭을 위한 정규화."""
    return re.sub(r"\s+", "", (s or "").strip().lower())


def _candidate_map() -> dict[str, str]:
    """정규화된 이름/별칭/제품명 → 표준 유효성분명(name_en) 매핑."""
    cand: dict[str, str] = {}
    for row in _load("active_ingredients.json").get("active_ingredients", []):
        en = row.get("name_en", "")
        for name in [en, row.get("name_ko", ""), *row.get("aliases", [])]:
            if name:
                cand[_norm(name)] = en
    for p in _load("products.json").get("products", []):
        if p.get("product_name"):
            cand[_norm(p["product_name"])] = p.get("active_ingredient")
    return cand


def resolve_ingredient(query: str) -> str | None:
    """제품명/성분명(영문·한글·별칭·표기변형) → 표준 유효성분명. 못 찾으면 None.

    매칭 순서: 정확 일치 → 부분 포함 → 유사도(오타·표기변형 허용).
    """
    q = _norm(query)
    if not q:
        return None
    cand = _candidate_map()

    if q in cand:                                   # 1) 정확 일치
        return cand[q]
    for key, en in cand.items():                    # 2) 부분 포함
        if q in key or key in q:
            return en
    match = difflib.get_close_matches(q, list(cand), n=1, cutoff=0.6)  # 3) 유사도
    if match:
        return cand[match[0]]
    return None


def product_name_for(ingredient: str) -> str | None:
    """유효성분명 → 등록 제품명(대표). 없으면 None."""
    for p in _load("products.json").get("products", []):
        if p.get("active_ingredient", "").lower() == ingredient.lower():
            return p.get("product_name")
    return None


def find_ingredient_in_text(text: str) -> str | None:
    """문장 안에서 등록된 성분/제품명을 찾아 표준 유효성분명 반환. 없으면 None.

    문장형 질의("헥시티아족스 다음엔 뭐 쳐요?", "코드원 쓰고 다음")에서 성분 추출용.
    긴 이름부터 부분일치해 오탐을 줄인다.
    """
    q = _norm(text)
    if not q:
        return None
    cand = _candidate_map()
    for key in sorted(cand, key=len, reverse=True):
        if len(key) >= 3 and key in q:
            return cand[key]
    return None


def parse_spray_time(text: str | None) -> str | None:
    """살포시각 입력을 ISO 문자열로. ISO 그대로거나 자연어("N시간 전","방금","어제")를 허용.

    파싱 실패 시 None (→ 안전시각 계산 생략).
    """
    if not text:
        return None
    t = text.strip()
    try:
        return datetime.fromisoformat(t).isoformat()   # 이미 ISO
    except ValueError:
        pass

    now = datetime.now()
    if t in ("지금", "방금", "방금 전"):
        return now.isoformat()
    if "어제" in t:
        return (now - timedelta(days=1)).isoformat()

    m = re.search(r"(\d+)\s*(분|시간|일)\s*전", t)       # "5시간 전", "30분 전", "2일 전"
    if m:
        n, unit = int(m.group(1)), m.group(2)
        delta = {"분": timedelta(minutes=n), "시간": timedelta(hours=n), "일": timedelta(days=n)}[unit]
        return (now - delta).isoformat()
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
