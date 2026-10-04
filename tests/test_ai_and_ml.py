from conftest import login, take_diagnostic


def test_mock_tutor_is_contextual_and_grounded(client):
    h = login(client, "meera@demo.eduadapt.ai")
    tid = client.get("/student/roadmap/next-topic", headers=h).json()["recommendation"]["topic_id"]
    r = client.post("/ai/chat", headers=h, json={"message": "Can you explain this with an example?", "topic_id": tid})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "mock" and body["sources"]
    assert body["context"]["level"] == "Intermediate" and body["context"]["topic"]
    again = client.post("/ai/chat", headers=h, json={"message": "Can you explain this with an example?",
                                                     "topic_id": tid, "session_id": body["session_id"]}).json()
    assert again["answer"] == body["answer"]          # mock mode is deterministic
    assert len(client.get(f"/ai/sessions/{body['session_id']}", headers=h).json()["messages"]) == 4


def test_rag_retrieves_relevant_lesson():
    from app.services import rag
    hits = rag.search("How does a hash map handle collisions?", skill="dsa", k=3)
    assert hits and any("hash" in (h["topic"] + h["text"]).lower() for h in hits)
    sql = rag.search("difference between WHERE and HAVING", k=3)
    assert any(h["skill"] == "sql" for h in sql)


def test_random_forest_predicts_all_three_targets():
    from ml.predict import predict
    weak = predict({"previous_score": 20, "recent_score": 25, "attempts": 2, "study_hours": 2, "completion_rate": 0.1,
                    "time_per_question": 80, "topic_mastery": 10, "goal": 0, "interest": 0, "difficulty": 1})
    strong = predict({"previous_score": 88, "recent_score": 92, "attempts": 30, "study_hours": 14,
                      "completion_rate": 0.9, "time_per_question": 20, "topic_mastery": 85, "goal": 1,
                      "interest": 1, "difficulty": 3.5})
    assert weak["learning_level"] == "Beginner" and strong["learning_level"] == "Advanced"
    assert weak["support_level"] == "High" and strong["support_level"] == "Low"
    assert 0 < strong["confidence"] <= 1


def test_another_language_end_to_end(client, new_student):
    quiz, result = take_diagnostic(client, new_student, "cpp", correct_first=6)
    assert len(quiz["questions"]) == 20
    rec = client.get("/student/roadmap/next-topic?skill=cpp", headers=new_student).json()["recommendation"]
    topic = client.get(f"/topics/{rec['topic_id']}", headers=new_student).json()
    assert topic["skill"] == "cpp" and topic["resources"] and topic["objectives"]
    chat = client.post("/ai/chat", headers=new_student, json={"message": "give me a hint", "topic_id": rec["topic_id"]})
    assert chat.status_code == 200 and "Hint" in chat.json()["answer"]


def test_admin_weights_and_retrain(client):
    a = login(client, "admin@eduadapt.ai", "admin1234")
    w = client.put("/admin/weights", headers=a, json={"knowledge_gap": 3, "goal_relevance": 2,
                                                       "prerequisite_priority": 1.5, "recent_performance": 1,
                                                       "interest_match": 1, "difficulty_fit": 1, "feedback": 0.5}).json()
    assert abs(sum(w.values()) - 1) < 1e-6 and abs(w["knowledge_gap"] - 0.3) < 1e-6
