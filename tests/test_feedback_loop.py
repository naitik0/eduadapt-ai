from conftest import answer_key, login, take_diagnostic


def _topic(view, title):
    return next(t for l in view["levels"] for t in l["topics"] if t["title"] == title)


def test_quiz_updates_mastery_unlocks_and_replans(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=0)
    view = client.get("/student/roadmap", headers=new_student).json()
    first, second = _topic(view, "Python Introduction"), _topic(view, "Installation and Environment")
    assert second["status"] == "LOCKED"
    plan_before = client.get("/study-plan", headers=new_student).json()

    assert client.post(f"/topics/{first['id']}/start", headers=new_student).status_code == 200
    done = client.post(f"/topics/{first['id']}/complete", headers=new_student).json()
    assert done["mastery_change"]["after"] > done["mastery_change"]["before"]

    quiz = client.get(f"/quiz?topic_id={first['id']}", headers=new_student).json()
    res = client.post("/quiz/submit", headers=new_student,
                      json={"quiz_id": quiz["quiz_id"], "answers": answer_key(quiz), "time_seconds": 90}).json()
    loop = res["loop"]
    assert res["score"] == 100
    assert loop["mastery_change"]["after"] >= 70
    assert "Installation and Environment" in loop["unlocked"]
    assert loop["pipeline"] == ["learning_event", "performance_update", "classification_update", "mastery_update",
                                "roadmap_update", "recommendation_update", "study_plan_update"]
    view = client.get("/student/roadmap", headers=new_student).json()
    assert _topic(view, "Python Introduction")["status"] in ("COMPLETED", "MASTERED")
    assert _topic(view, "Installation and Environment")["status"] == "AVAILABLE"
    plan_after = client.get("/study-plan", headers=new_student).json()
    assert plan_after["id"] != plan_before["id"]
    scheduled = {i["topic"] for d in plan_after["week"] for i in d["items"]}
    assert "Installation and Environment" in scheduled


def test_poor_quiz_needs_revision_and_weak_concepts(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=0)
    tid = _topic(client.get("/student/roadmap", headers=new_student).json(), "Python Introduction")["id"]
    quiz = client.get(f"/quiz?topic_id={tid}", headers=new_student).json()
    res = client.post("/quiz/submit", headers=new_student,
                      json={"quiz_id": quiz["quiz_id"], "answers": answer_key(quiz, 1)}).json()
    assert res["weak_concepts"]
    assert _topic(client.get("/student/roadmap", headers=new_student).json(),
                  "Python Introduction")["status"] == "NEEDS_REVISION"
    # resubmitting the same quiz is rejected
    assert client.post("/quiz/submit", headers=new_student,
                       json={"quiz_id": quiz["quiz_id"], "answers": {}}).status_code == 409


def test_locked_topics_cannot_be_started_or_quizzed(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=0)
    capstone = _topic(client.get("/student/roadmap", headers=new_student).json(), "AI-powered Capstone Project")
    assert capstone["status"] == "LOCKED"
    assert client.post(f"/topics/{capstone['id']}/start", headers=new_student).status_code == 409
    assert client.get(f"/quiz?topic_id={capstone['id']}", headers=new_student).status_code == 409


def test_adaptive_quiz_difficulty(client):
    beginner, advanced = login(client, "aarav@demo.eduadapt.ai"), login(client, "rohan@demo.eduadapt.ai")
    b_rec = client.get("/student/roadmap/next-topic", headers=beginner).json()["recommendation"]
    a_rec = client.get("/student/roadmap/next-topic", headers=advanced).json()["recommendation"]
    bq = client.get(f"/quiz?topic_id={b_rec['topic_id']}", headers=beginner).json()
    aq = client.get(f"/quiz?topic_id={a_rec['topic_id']}", headers=advanced).json()
    assert bq["difficulty"] < aq["difficulty"]
    assert len(bq["questions"]) <= len(aq["questions"])


def test_study_plan_respects_daily_budget(client):
    h = login(client, "sana@demo.eduadapt.ai")
    plan = client.post("/study-plan/generate", headers=h).json()
    daily = client.get("/student/profile", headers=h).json()["daily_minutes"]
    assert plan["today"]["items"]
    for day in plan["week"]:
        assert day["total_minutes"] <= daily
    item = plan["today"]["items"][0]
    assert client.patch(f"/study-plan/items/{item['id']}", headers=h, json={"done": True}).json()["done"] is True


def test_recommendation_feedback_shifts_score(client, new_student):
    take_diagnostic(client, new_student, "python", correct_first=12)
    recs = client.get("/recommendations", headers=new_student).json()["recommendations"]
    target = recs[0]
    client.post("/recommendations/feedback", headers=new_student,
                json={"recommendation_id": target["id"], "topic_id": target["topic_id"], "rating": -1})
    after = {r["topic_id"]: r for r in client.get("/recommendations", headers=new_student).json()["recommendations"]}
    if target["topic_id"] in after:
        assert after[target["topic_id"]]["components"]["feedback"] < target["components"]["feedback"]


def test_dashboard_analytics_use_real_data(client):
    h = login(client, "meera@demo.eduadapt.ai")
    a = client.get("/analytics", headers=h).json()
    assert a["topics_total"] == 55 and a["topics_done"] > 0
    assert a["quiz_performance"] and a["mastery_by_topic"]
    assert client.get("/progress", headers=h).status_code == 200
