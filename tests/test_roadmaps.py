from app.data.parser import all_roadmaps

EXPECTED = {"python", "java", "c", "cpp", "javascript", "typescript", "go", "rust", "kotlin", "csharp", "sql",
            "html-css", "react", "nodejs", "dsa", "machine-learning", "data-science"}


def test_all_skills_present(client):
    skills = {s["slug"]: s for s in client.get("/skills").json()}
    assert EXPECTED <= set(skills)
    assert skills["python"]["topics"] == 55


def test_levels_and_technology_specific_topics(client):
    py = client.get("/roadmaps/python").json()
    assert [l["name"] for l in py["levels"]] == ["Beginner", "Intermediate", "Advanced", "Projects"]
    titles = {s: {t["title"] for l in client.get(f"/roadmaps/{s}").json()["levels"] for t in l["topics"]}
              for s in ("python", "java", "cpp", "javascript", "sql")}
    assert {"Decorators", "Generators", "Context Managers"} <= titles["python"]
    assert {"Streams", "JVM Internals", "Spring Boot"} <= titles["java"]
    assert any("Pointer" in t for t in titles["cpp"]) and any("Move" in t for t in titles["cpp"])
    assert "Closures" in titles["javascript"] and any("Window" in t for t in titles["sql"])
    # roadmaps are not renamed copies of one another
    assert len(titles["java"] & titles["cpp"]) < 6


def test_prerequisite_graph_is_valid_and_acyclic():
    for skill, topics in all_roadmaps().items():
        names = {t["title"] for t in topics}
        order = {t["title"]: t["order"] for t in topics}
        for t in topics:
            for p in t["prereqs"]:
                assert p in names, (skill, t["title"], p)
                assert order[p] < order[t["title"]], f"{skill}: {t['title']} depends on later {p}"


def test_projects_have_milestones_and_criteria(client):
    projects = client.get("/projects?skill=python").json()
    assert len(projects) == 7
    for p in projects:
        assert p["milestones"] and p["evaluation_criteria"] and p["requirements"]
