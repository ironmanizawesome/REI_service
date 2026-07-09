from app.calculator import build_rei_table as _compute_rei_table


def build_rei_table() -> tuple[dict, list[str]]:
    """REI 표를 calculator.py로 직접 계산해 제공한다.

    [성분][작업유형][시간][보호장비] 전 조합을 EFSA 계산식으로 산출하므로
    보호장비 3단계와 모든 작업시간(수확 1~8h, 예찰 1~2h)이 채워지고
    누락(missing) 조합이 없다.

    (data/rei_results.json 은 '없음' 기준값 스냅샷으로, 참고·검증용으로만 유지.
     calculator.py 산출값이 이 스냅샷과 일치함을 확인함.)
    """
    return _compute_rei_table(), []
