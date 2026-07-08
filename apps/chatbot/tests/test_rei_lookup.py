"""REI 룩업·엔드포인트 회귀 테스트 (키 없이 폴백 경로로 동작).

실행: cd apps/chatbot && pip install pytest && pytest
"""

from fastapi.testclient import TestClient

from app import rei_lookup as R
from app.main import app

client = TestClient(app)


# ---------- 룩업 로직 ----------
def test_resolve_ingredient_by_name():
    assert R.resolve_ingredient("Bifenazate") == "Bifenazate"
    assert R.resolve_ingredient("없는성분") is None


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
