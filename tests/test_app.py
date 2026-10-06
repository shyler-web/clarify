def test_index_renders_repo_and_worst_files(tmp_path):
    from fastapi.testclient import TestClient
    from paydown.app import create_app
    app = create_app(project_path=str(tmp_path))
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "Cognitive-Debt" in r.text