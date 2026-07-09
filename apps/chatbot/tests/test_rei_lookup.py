"""REI 룩업·엔드포인트 회귀 테스트 (키 없이 폴백 경로로 동작).

실행: cd apps/chatbot && pip install pytest && pytest
"""

from fastapi.testclient import TestClient

from chatbot_app import rei_lookup as R
from chatbot_app import rotation
from chatbot_app.main import app

client = TestClient(app)


# ---------- 룩업 로직 ----------
def test_resolve_ingredient_by_name():
    assert R.resolve_ingredient("Bifenazate") == "Bifenazate"
    assert R.resolve_ingredient("없는성분") is None


def test_resolve_ingredient_korean_and_fuzzy():
    # 한글 표기·별칭·오타 허용
    assert R.resolve_ingredient("비페나제이트") == "Bifenazate"
    assert R.resolve_ingredient("바이펜아제이트") == "Bifenazate"   # 별칭
    assert R.resolve_ingredient("바이펜아제잍") == "Bifenazate"     # 오타(유사도)
    assert R.resolve_ingredient("아세타미프리드") == "Acetamiprid"


def test_parse_spray_time():
    assert R.parse_spray_time("2026-07-03T09:00:00") == "2026-07-03T09:00:00"
    assert R.parse_spray_time("5시간 전") is not None      # 자연어 상대시각
    assert R.parse_spray_time("방금") is not None
    assert R.parse_spray_time("아무거나") is None          # 해석 불가 → None
    assert R.parse_spray_time(None) is None


def test_lookup_known_value():
    # data/rei_results.json 기준: Bifenazate 수확 6h = 101.8
    r = R.lookup_rei("Bifenazate", "수확", 6)
    assert r["rei_hours"] == 101.8
    assert r["work_hours_used"] == 6


def test_lookup_defaults_to_most_conservative():
    # 작업시간 미지정 → 최대 REI(8h=122.2)
    r = R.lookup_rei("Bifenazate", "수확")
    assert r["rei_hours"] == 122.2
    assert r["work_hours_used"] == 8


def test_lookup_zero_rei():
    # Spirodiclofen 전 구간 0
    assert R.lookup_rei("Spirodiclofen", "수확", 8)["rei_hours"] == 0


def test_lookup_missing_work_type():
    r = R.lookup_rei("Bifenazate", "적엽")
    assert r["rei_hours"] is None
    assert "적엽" in r["note"]


def test_safe_reentry_time():
    # 07/03 09:00 + 101.8h = 07/07 14:48
    assert R.safe_reentry_time("2026-07-03T09:00:00", 101.8) == "2026-07-07T14:48:00"


# ---------- 엔드포인트 ----------
def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_suggested_questions():
    qs = client.get("/suggested-questions").json()["questions"]
    assert len(qs) >= 1


def test_rei_endpoint_full_flow():
    resp = client.post("/rei", json={
        "product": "Bifenazate", "work_type": "수확",
        "work_hours": 6, "spray_time": "2026-07-03T09:00:00",
    }).json()
    assert resp["rei_hours"] == 101.8
    assert resp["safe_time"] == "2026-07-07T14:48:00"
    # 해석은 숫자를 그대로 인용해야 함
    assert "101.8" in resp["explanation"]


def test_rei_endpoint_unknown_product():
    resp = client.post("/rei", json={"product": "사파이어", "work_type": "수확"}).json()
    assert resp["ingredient"] is None
    assert resp["rei_hours"] is None


def test_chat_fallback():
    resp = client.post("/chat", json={"message": "테스트"}).json()
    assert "answer" in resp


# ---------- 로테이션 엔진 ----------
def test_rotation_infers_pest_and_excludes_last():
    # 헥시티아족스(점박이응애, IRAC 10A) 사용 후 → 같은 응애 타깃, 다른 그룹 추천
    r = rotation.recommend_rotation(history=["Hexythiazox"])
    assert r["target_pest"] == "점박이응애"
    names = [x["ingredient"] for x in r["recommendations"]]
    assert "Hexythiazox" not in names                      # 직전 사용 제외
    assert {"Fenpyroximate", "Spirodiclofen", "Bifenazate"} <= set(names)
    assert all(x["recommended"] for x in r["recommendations"])  # 전부 다른 IRAC


def test_rotation_korean_input():
    r = rotation.recommend_rotation(history=["바이펜아제이트"])  # 한글 별칭
    assert r["target_pest"] == "점박이응애"
    assert "Bifenazate" not in [x["ingredient"] for x in r["recommendations"]]


def test_rotation_fruit_fly_pair():
    # 과실파리류 = 아세타미프리드·클로란트라닐리프롤 2종 → 서로 로테이션 가능
    r = rotation.recommend_rotation(history=["Acetamiprid"])
    assert r["target_pest"] == "과실파리류"
    names = [x["ingredient"] for x in r["recommendations"]]
    assert names == ["Chlorantraniliprole"]
    assert r["recommendations"][0]["recommended"]  # 다른 IRAC(28 vs 4A)


def test_rotation_includes_product_name():
    # 추천에 제품명이 함께 담겨야 함 (Fenpyroximate → 살비왕)
    r = rotation.recommend_rotation(history=["Hexythiazox"])
    by_ing = {x["ingredient"]: x for x in r["recommendations"]}
    assert by_ing["Fenpyroximate"]["product"] == "살비왕"
    assert by_ing["Bifenazate"]["product"] == "코드원"


def test_rotation_endpoint():
    resp = client.post("/rotation", json={"history": ["Hexythiazox"]}).json()
    assert resp["target_pest"] == "점박이응애"
    assert "recommendations" in resp


# ---------- 챗봇 로테이션 인텐트 라우팅 ----------
def test_rotation_intent_detection():
    assert rotation.detect_rotation_intent("헥시티아족스 다음엔 뭐 쳐요?")
    assert rotation.detect_rotation_intent("농약 번갈아 쓰는 거 추천해줘")
    assert not rotation.detect_rotation_intent("재출입 제한시간이 뭐예요?")


def test_find_ingredient_in_text():
    assert R.find_ingredient_in_text("헥시티아족스 다음엔 뭐 쳐요?") == "Hexythiazox"
    assert R.find_ingredient_in_text("코드원 쓰고 다음에는?") == "Bifenazate"  # 제품명
    assert R.find_ingredient_in_text("오늘 날씨 어때") is None


def test_chat_routes_rotation():
    # 로테이션 질문 → 추천 약제가 답변에 포함 (RAG 아님)
    resp = client.post("/chat", json={"message": "헥시티아족스 다음엔 뭐 쳐요?"}).json()
    assert ("펜피록시메이트" in resp["answer"]) or ("추천 약제" in resp["answer"])
    assert resp["sources"] == []


def test_chat_rotation_without_ingredient():
    resp = client.post("/chat", json={"message": "농약 다음에 뭐 쳐요?"}).json()
    assert "알려주시면" in resp["answer"]
