from conftest import login


def test_register_login_and_profile(client):
    r = client.post("/auth/register", json={"name": "Ada", "email": "ada@test.io", "password": "password123"})
    assert r.status_code == 201
    assert r.json()["user"]["onboarded"] is False
    h = login(client, "ada@test.io", "password123")
    p = client.get("/student/profile", headers=h).json()
    assert p["email"] == "ada@test.io" and "goals" in p["options"]


def test_duplicate_and_bad_credentials(client):
    client.post("/auth/register", json={"name": "Bo", "email": "bo@test.io", "password": "password123"})
    assert client.post("/auth/register", json={"name": "Bo", "email": "bo@test.io",
                                                "password": "password123"}).status_code == 409
    assert client.post("/auth/login", json={"email": "bo@test.io", "password": "wrong-pass"}).status_code == 401


def test_protected_routes_need_token(client):
    assert client.get("/student/profile").status_code in (401, 403)
    assert client.get("/recommendations").status_code in (401, 403)


def test_admin_only(client):
    h = login(client, "aarav@demo.eduadapt.ai")
    assert client.get("/admin/overview", headers=h).status_code == 403
    a = login(client, "admin@eduadapt.ai", "admin1234")
    assert client.get("/admin/overview", headers=a).status_code == 200
