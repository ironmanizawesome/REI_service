# rei_core — 공용 REI 계산 로직

챗봇·텔레그램·웹이 공통으로 참조하는 REI 계산 모듈.

## 함수

- `toxicity_default_rei(category)` — EPA PRN 95-3 기본 REI (Layer 1)
- `method_b_rei(category, dt50_days, ref_dt50_days=3.0)` — **현재 기본 방식**. EPA 기본 REI × DT50 보정
- `method_a_rei(MethodAInputs)` — 박연기(2021) 폐쇄형 로그 수식 (실험/참고용, DAF 불안정)

## 사용 예

```python
from rei_core import method_b_rei, toxicity_default_rei

toxicity_default_rei(2)              # 24 (시간)
method_b_rei(2, dt50_days=5.0)       # 40.0 (시간)
```

## 위치 (중요)

**최종 서비스의 REI 값은 이 모듈이 아니라 `data/rei_results.json` 룩업 테이블에서 온다.** 팀이 EFSA 2022 Guidance로 직접 산정했기 때문. 아래 계산 함수(Method A/B, DT50 보정)는 **참고용으로 유지**한다 — 발표에서 "이 방식을 시도했다 접었다"의 근거이자, 향후 재검토 여지. 버리지 않음.

## 주의

`calc.py`의 기본값은 뼈대용. Method A는 단위 정합 재확인 필요. 실제 산정 로직은 팀 계산(EFSA)으로 대체됨.
