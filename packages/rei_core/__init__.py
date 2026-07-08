"""rei_core — 공용 REI 계산 로직.

현재 기본 방식은 Method B (EPA 기본 REI × DT50 감쇠 보정).
Method A(직접 로그 수식)는 참고/실험용으로 함께 제공.
"""

from .calc import (
    DEFAULT_REI_HOURS,
    method_a_rei,
    method_b_rei,
    toxicity_default_rei,
)

__all__ = [
    "DEFAULT_REI_HOURS",
    "toxicity_default_rei",
    "method_a_rei",
    "method_b_rei",
]
