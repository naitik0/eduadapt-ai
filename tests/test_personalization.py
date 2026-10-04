from conftest import DEMO, login, take_diagnostic


def test_demo_students_classified_and_recommended_differently(client):
    tops = {}
    for key, (email, skill, level) in DEMO.items():
        h = login(client, email)
        prof = client.get("/student/profile", headers=h).json()
        assert prof["learning_level"] == level, (key, prof["learning_level"])
        recs = client.get("/recommendations", headers=h).json()["recommendations"]
        assert recs and all(r["reason"] for r in recs)
        tops[key] = recs[0]["title"]
        assert client.get("/student/roadmap", headers=h).json()["skill"] == skill
    assert len(set(tops.values())) == len(tops), tops


def test_diagnostic_has_20_questions_across_levels(client, new_student):
    quiz, result = take_diagnostic(client, new_student, "python", correct_first=10)
    assert len(quiz["questions"]) == 20
    assert result["total"] == 20 and "placement" in result
    assert result["loop"]["pipeline"][-1] == "study_plan_update"
    prof = client.get("/student/profile", headers=new_student).json()
    assert prof["onboarded"] and prof["classification_confidence"] > 0


def test_stronger_diagnostic_starts_further_along(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=0)
    weak = client.get("/student/roadmap", headers=new_student).json()
    from conftest import _n  # second student
    r = client.post("/auth/register", json={"name": "Strong", "email": "strong@test.io", "password": "password123"})
    strong_h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    take_diagnostic(client, strong_h, "python", correct_first=None)
    strong = client.get("/student/roadmap", headers=strong_h).json()
    assert strong["avg_mastery"] > weak["avg_mastery"] + 20

    def open_titles(v):
        return {t["title"] for l in v["levels"] for t in l["topics"] if t["status"] != "LOCKED"}
    assert "OOP" in open_titles(strong) and "OOP" not in open_titles(weak)
    weak_next = client.get("/student/roadmap/next-topic", headers=new_student).json()["recommendation"]
    assert weak_next["level"] == "Beginner"


def test_recommendation_components_follow_weights(client):
    h = login(client, "meera@demo.eduadapt.ai")
    data = client.get("/recommendations", headers=h).json()
    w = data["weights"]
    assert abs(sum(w.values()) - 1) < 1e-6
    for r in data["recommendations"]:
        total = sum(w[k] * v for k, v in r["components"].items()) * 100
        assert abs(total - r["score"]) < 0.6
        assert r["status"] != "LOCKED"


def test_profile_goal_change_reranks(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=14)
    before = client.get("/recommendations", headers=new_student).json()["recommendations"]
    client.put("/student/profile", headers=new_student, json={"goal": "web_development", "interests": ["web"]})
    after = client.get("/recommendations", headers=new_student).json()["recommendations"]
    assert [r["score"] for r in before] != [r["score"] for r in after]
