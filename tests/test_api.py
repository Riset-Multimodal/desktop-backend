from tests.conftest import login


def _tlx(**extra):
    body = {f"pair_q{i}": "mental" for i in range(1, 16)}
    body.update(likert_mental=50, likert_physical=10, likert_temporal=20,
                likert_performance_raw=100, likert_effort=30, likert_frustration=40)
    body.update(extra)
    return body


def _nordic(**extra):
    body = {f"nbm_{i}": 1 for i in range(28)}
    body.update(extra)
    return body


def test_login(client):
    assert login(client).status_code == 200
    assert login(client, password="salah").status_code == 401
    assert login(client, email="tidakada@test.com").status_code == 401


def test_endpoints_require_auth(client):
    for method, path in [("get", "/users"), ("get", "/tlx"), ("get", "/nordic"), ("get", "/validation"),
                         ("post", "/keylogger"), ("post", "/tlx")]:
        assert getattr(client, method)(path).status_code == 401, path


def test_users_admin_only(client, auth, admin):
    assert client.get("/users", headers=auth).status_code == 403
    res = client.get("/users", headers=admin)
    assert res.status_code == 200
    # user tanpa nama tidak lagi membuat endpoint ini 500
    assert {u["user_email"] for u in res.json()} >= {"peserta@test.com", "lain@test.com"}
    assert client.get("/users/me", headers=auth).json()["name"] == "Peserta"


def test_keylogger_uses_token_email_and_safe_path(client, auth):
    res = client.post("/keylogger", headers=auth, json={"features": {"keystroke_count": 3, "type": "realtime"}})
    assert res.status_code == 200
    assert res.json()["data"]["saved_to"].startswith("logs/peserta@test.com_keylogger/")
    res = client.post("/keylogger", headers=auth, json={"email": "lain@test.com", "features": {}})
    assert res.status_code == 403


def test_questionnaire_atomic_and_scoped(client, auth, admin):
    res = client.post("/questionnaire", headers=auth, json={
        "tlx": _tlx(user_email="peserta@test.com"),
        "nordic": _nordic(),
        "validation": {"answer": "FOCUS_TASK"},
    })
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["tlx"]["likert_performance"] == 1
    assert body["nordic"]["nbm_27"] == 1 and body["nordic"]["total_score"] == 28

    # nordic invalid -> tidak ada TLX yang ikut tersimpan
    before = len(client.get("/tlx", headers=auth).json())
    res = client.post("/questionnaire", headers=auth, json={
        "tlx": _tlx(), "nordic": _nordic(nbm_3=0), "validation": {"answer": "FOCUS_TASK"},
    })
    assert res.status_code == 422
    assert len(client.get("/tlx", headers=auth).json()) == before

    # user tidak bisa melihat data user lain
    assert client.get("/tlx?email=lain@test.com", headers=auth).status_code == 403
    nbm_id = body["nordic"]["id"]
    other = {"Authorization": "Bearer " + login(client, email="lain@test.com").json()["access_token"]}
    assert client.get(f"/nordic/{nbm_id}", headers=other).status_code == 404
    assert client.get(f"/nordic/{nbm_id}", headers=admin).status_code == 200


def test_health_hides_errors(client):
    assert client.get("/health").status_code == 200


def test_posture_requires_auth_and_sanitizes(client, auth, tmp_root):
    files = {k: (f"{k}.jpg", b"\xff\xd8notreallyjpeg", "image/jpeg") for k in ("front_image", "side_image", "overhead_image")}
    assert client.post("/posture", data={"capture_id": "x"}, files=files).status_code == 401
    res = client.post("/posture", headers=auth, data={"capture_id": "../../evil"}, files=files)
    # analisis gagal (gambar palsu), tapi file hanya boleh tersimpan di folder user
    assert res.status_code == 422
    saved = list((tmp_root / "data").rglob("*evil*"))
    assert saved and all("peserta@test.com_posture" in str(p) for p in saved)
