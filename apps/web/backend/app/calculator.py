# 이 수식은 data/rei_results.json이 어떻게 산출되었는지 보여주는 참고 구현입니다.
# 실제 서빙되는 값은 항상 rei_results.json을 따릅니다 (app/rei_data.py 참고).

import math

BW = 64.0  # kg, 고정값

COMPOUNDS = {
    "Hexythiazox":         {"ar": 0.0338, "dt50_tr": 6.36,  "aoel": 0.009,  "daf": 0.055,  "product": "붐"},
    "Fenpyroximate":       {"ar": 0.0338, "dt50_tr": 7.15,  "aoel": 0.005,  "daf": 0.055,  "product": "살비왕"},
    "Spirodiclofen":       {"ar": 0.0405, "dt50_tr": 5.25,  "aoel": 0.009,  "daf": 0.017,  "product": "응애엔"},
    "Bifenazate":          {"ar": 0.1600, "dt50_tr": 6.13,  "aoel": 0.0036, "daf": 0.015,  "product": "코드원"},
    "Acetamiprid":         {"ar": 0.0450, "dt50_tr": 6.10,  "aoel": 0.025,  "daf": 0.248,  "product": "모스피란"},
    "Chlorantraniliprole": {"ar": 0.0390, "dt50_tr": 11.70, "aoel": 0.36,   "daf": 0.0295, "product": "비대위"},
}

TASKS = {
    "수확":  {"tc": 22500, "max_hours": 8, "hour_options": [1, 2, 3, 4, 5, 6, 7, 8]},
    "예찰":  {"tc": 12500, "max_hours": 2, "hour_options": [1, 2]},
}

PPE_MULTIPLIER = {
    "없음": 1.0,
    "작업복만": 0.2,
    "작업복+장갑": 0.1,
}


def calc_rei_hours(ar_kg_ha: float, dt50_tr_days: float, aoel: float, daf: float,
                    tc: float, hours: float, ppe_multiplier: float) -> float:
    dfr0 = 3.0 * ar_kg_ha
    dt50_dfr = dt50_tr_days / 3.0  # TR(과실잔류) -> DFR(엽면잔류) 보정
    k = math.log(2) / dt50_dfr
    E0 = dfr0 * tc * hours * daf * ppe_multiplier / (1000 * BW)
    R = E0 / aoel
    if R <= 1:
        return 0.0
    return (math.log(R) / k) * 24  # 일 단위 k를 시간 단위로 환산


def build_compound_products() -> dict:
    return {compound: params["product"] for compound, params in COMPOUNDS.items()}


def build_rei_table() -> dict:
    table = {}
    for compound, params in COMPOUNDS.items():
        table[compound] = {}
        for task_name, task_params in TASKS.items():
            table[compound][task_name] = {}
            for hours in task_params["hour_options"]:
                table[compound][task_name][str(hours)] = {
                    ppe_name: calc_rei_hours(
                        ar_kg_ha=params["ar"],
                        dt50_tr_days=params["dt50_tr"],
                        aoel=params["aoel"],
                        daf=params["daf"],
                        tc=task_params["tc"],
                        hours=hours,
                        ppe_multiplier=ppe_multiplier,
                    )
                    for ppe_name, ppe_multiplier in PPE_MULTIPLIER.items()
                }
    return table
