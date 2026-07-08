"""REI 계산 함수.

수식 출처:
- 폐쇄형 로그 REI 식: 박연기(2021) — EPA/EFSA는 표 기반 MOE 접근만 제시.
    REI = (1/k) · ln[(DFR0 · TC · H) / (BW · AOEL)]
- Layer 1 기본 REI: EPA PRN 95-3 (1995), 급성독성 카테고리 기반 4/12/24/48h.
- Method B: EPA 기본 REI를 앵커로 두고 DT50 감쇠로 보정 (DAF 변동성 회피).

주의: 아래 값들은 뼈대용 기본값이다. 실제 값은 data/ 의 검증 데이터로 대체할 것.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# EPA PRN 95-3 급성독성 카테고리별 기본 REI (시간)
DEFAULT_REI_HOURS: dict[int, int] = {
    1: 48,  # Category I  (가장 독성 높음)
    2: 24,  # Category II
    3: 12,  # Category III
    4: 4,   # Category IV
}


def toxicity_default_rei(toxicity_category: int) -> int:
    """급성독성 카테고리(I~IV) → EPA 기본 REI(시간). Layer 1."""
    if toxicity_category not in DEFAULT_REI_HOURS:
        raise ValueError(f"toxicity_category must be 1-4, got {toxicity_category}")
    return DEFAULT_REI_HOURS[toxicity_category]


@dataclass
class MethodAInputs:
    dfr0: float       # 초기 dislodgeable foliar residue (µg/cm²)
    tc: float         # transfer coefficient (cm²/hr)
    h: float          # 작업 시간 (hr/day)
    bw: float         # 체중 (kg)
    aoel: float       # acceptable operator exposure level (mg/kg bw/day)
    k: float          # 잔류 감쇠 상수 (1/day); k = ln2 / DT50


def method_a_rei(inp: MethodAInputs) -> float:
    """Method A — 폐쇄형 로그 수식 (박연기 2021).

    REI = (1/k) · ln[(DFR0 · TC · H) / (BW · AOEL)]  [days]

    ⚠️ DAF 변동성으로 화합물 간 극단적 불안정(0h~114h). 실험/참고용.
    단위 정합은 실제 데이터 연결 시 재확인 필요.
    """
    numerator = inp.dfr0 * inp.tc * inp.h
    denominator = inp.bw * inp.aoel
    ratio = numerator / denominator
    if ratio <= 1:
        return 0.0
    return (1.0 / inp.k) * math.log(ratio)


def method_b_rei(toxicity_category: int, dt50_days: float, ref_dt50_days: float = 3.0) -> float:
    """Method B — EPA 기본 REI × DT50 감쇠 보정 (현재 기본 방식).

    안정적 범위 산출. 기준 반감기(ref_dt50_days) 대비 실제 반감기 비율로 보정.

    return: 보정된 REI (시간)
    """
    base = toxicity_default_rei(toxicity_category)
    if ref_dt50_days <= 0:
        raise ValueError("ref_dt50_days must be > 0")
    correction = dt50_days / ref_dt50_days
    return base * correction
