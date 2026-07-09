import json
from pathlib import Path

from app.calculator import COMPOUNDS, PPE_MULTIPLIER, TASKS

REPO_ROOT = Path(__file__).resolve().parents[4]
REI_RESULTS_PATH = REPO_ROOT / "data" / "rei_results.json"


def _load_raw_results() -> dict:
    with open(REI_RESULTS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return {entry["active_ingredient"]: entry["by_work_type"] for entry in raw["results"]}


def build_rei_table() -> tuple[dict, list[str]]:
    """data/rei_results.json을 프론트엔드가 쓰는 [성분][작업유형][시간][보호장비] 형태로 캐싱한다.

    rei_results.json에는 보호장비별 값이 없어(성분×작업유형×시간 단위까지만 존재),
    당장은 '없음' 기준값을 세 단계 보호장비에 동일하게 채워 넣고 missing 목록으로 보고한다.
    시간 자체가 없는 조합(예: 수확 3/5/7시간)은 서빙하지 않고 missing 목록에만 남긴다.
    """
    by_compound = _load_raw_results()
    table = {}
    missing = []

    for compound in COMPOUNDS:
        table[compound] = {}
        compound_data = by_compound.get(compound)
        if compound_data is None:
            missing.append(f"{compound}: rei_results.json에 성분 자체가 없음")
            continue

        for task_name, task_params in TASKS.items():
            table[compound][task_name] = {}
            task_data = compound_data.get(task_name, {})

            for hours in task_params["hour_options"]:
                hours_key = str(hours)
                if hours_key not in task_data:
                    missing.append(f"{compound} / {task_name} / {hours}시간: 데이터 자체 없음")
                    continue

                base_rei = task_data[hours_key]
                table[compound][task_name][hours_key] = {ppe_name: base_rei for ppe_name in PPE_MULTIPLIER}
                missing.append(
                    f"{compound} / {task_name} / {hours}시간: 보호장비별 값 없음 "
                    f"(현재 '없음' 기준값 {base_rei}로 3단계 모두 대체 중)"
                )

    return table, missing
