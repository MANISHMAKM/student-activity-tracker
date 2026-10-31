import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as app_module  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # use a fresh temporary database for every test
    monkeypatch.setattr(app_module, "DB_NAME", str(tmp_path / "test.db"))
    app_module.create_table()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def add(client, name="Asha", activity="Football", hours=2):
    return client.post("/activities", json={"name": name, "activity": activity, "hours": hours})


# ---------------------------------------------------------------- POST
def test_add_activity_success(client):
    res = add(client)
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] == 1
    assert body["name"] == "Asha"
    assert body["activity"] == "Football"
    assert body["hours"] == 2


def test_add_activity_decimal_hours(client):
    res = add(client, hours=1.5)
    assert res.status_code == 201
    assert res.get_json()["hours"] == 1.5


def test_add_activity_trims_whitespace(client):
    res = add(client, name="  Asha  ", activity="  Chess ")
    assert res.get_json()["name"] == "Asha"
    assert res.get_json()["activity"] == "Chess"


@pytest.mark.parametrize(
    "payload,field",
    [
        ({"activity": "x", "hours": 1}, "name"),
        ({"name": "", "activity": "x", "hours": 1}, "name"),
        ({"name": "   ", "activity": "x", "hours": 1}, "name"),
        ({"name": 123, "activity": "x", "hours": 1}, "name"),
        ({"name": "A", "hours": 1}, "activity"),
        ({"name": "A", "activity": "", "hours": 1}, "activity"),
        ({"name": "A", "activity": "x"}, "hours"),
        ({"name": "A", "activity": "x", "hours": "abc"}, "hours"),
        ({"name": "A", "activity": "x", "hours": "2"}, "hours"),
        ({"name": "A", "activity": "x", "hours": 0}, "hours"),
        ({"name": "A", "activity": "x", "hours": -3}, "hours"),
        ({"name": "A", "activity": "x", "hours": 25}, "hours"),
        ({"name": "A", "activity": "x", "hours": True}, "hours"),
        ({"name": "A", "activity": "x", "hours": None}, "hours"),
    ],
)
def test_add_activity_validation_errors(client, payload, field):
    res = client.post("/activities", json=payload)
    assert res.status_code == 400
    assert field in res.get_json()["details"]


def test_add_activity_reports_all_errors_at_once(client):
    res = client.post("/activities", json={})
    assert res.status_code == 400
    assert set(res.get_json()["details"]) == {"name", "activity", "hours"}


def test_add_activity_invalid_json(client):
    res = client.post("/activities", data="not json", content_type="application/json")
    assert res.status_code == 400


def test_add_activity_no_body(client):
    assert client.post("/activities").status_code == 400


def test_add_activity_json_array_rejected(client):
    res = client.post("/activities", json=[1, 2, 3])
    assert res.status_code == 400


# ----------------------------------------------------------------- GET
def test_list_empty(client):
    res = client.get("/activities")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_returns_all_newest_first(client):
    add(client, name="A")
    add(client, name="B")
    data = client.get("/activities").get_json()
    assert [a["name"] for a in data] == ["B", "A"]


# ------------------------------------------------------------- SUMMARY
def test_summary_empty(client):
    res = client.get("/summary")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total_entries"] == 0
    assert body["total_hours"] == 0
    assert body["most_active_user"] is None


def test_summary_values(client):
    add(client, name="Asha", hours=2)
    add(client, name="Ben", hours=1.5)
    add(client, name="Asha", hours=3)
    body = client.get("/summary").get_json()
    assert body["total_entries"] == 3
    assert body["total_hours"] == 6.5
    assert body["most_active_user"] == "Asha"
    assert body["most_active_user_hours"] == 5


def test_summary_most_active_is_by_hours_not_entries(client):
    add(client, name="Asha", hours=1)
    add(client, name="Asha", hours=1)
    add(client, name="Ben", hours=5)
    assert client.get("/summary").get_json()["most_active_user"] == "Ben"


def test_summary_name_is_case_insensitive(client):
    add(client, name="asha", hours=2)
    add(client, name="Asha", hours=2)
    add(client, name="Ben", hours=3)
    body = client.get("/summary").get_json()
    assert body["most_active_user"].lower() == "asha"
    assert body["most_active_user_hours"] == 4


def test_summary_tie_is_deterministic(client):
    add(client, name="Ben", hours=2)
    add(client, name="Asha", hours=2)
    assert client.get("/summary").get_json()["most_active_user"] == "Asha"


# -------------------------------------------------------------- DELETE
def test_delete_activity(client):
    add(client)
    res = client.delete("/activities/1")
    assert res.status_code == 200
    assert client.get("/activities").get_json() == []


def test_delete_missing_returns_404(client):
    res = client.delete("/activities/999")
    assert res.status_code == 404
    assert "error" in res.get_json()


# --------------------------------------------------------------- ERRORS
def test_unknown_route_returns_json_404(client):
    res = client.get("/nope")
    assert res.status_code == 404
    assert res.is_json


def test_wrong_method_returns_json_405(client):
    res = client.put("/activities")
    assert res.status_code == 405
    assert res.is_json


def test_cors_header_present(client):
    res = client.get("/activities", headers={"Origin": "http://localhost:5173"})
    assert res.headers.get("Access-Control-Allow-Origin") in ("*", "http://localhost:5173")
