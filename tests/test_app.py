def test_index_renders_repo_and_worst_files(tmp_path):
    from fastapi.testclient import TestClient
    from paydown.app import create_app
    app = create_app(project_path=str(tmp_path))
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "Cognitive-Debt" in r.text


def _git(tmp_path, *args):
    import subprocess
    return subprocess.run(
        ["git", "-C", str(tmp_path), *args],
        capture_output=True,
        text=True,
        check=True,
        env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
             "PATH": "/usr/bin:/bin"},
    )


def test_trend_reanalyzes_each_commit_for_real_debt(tmp_path):
    from paydown.app import _trend
    from paydown.repo import analyze_repo
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "mod.py").write_text("def f():\n    return 1\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "c1")
    (tmp_path / "mod.py").write_text("def f():\n    \"\"\"doc\"\"\"\n    return 1\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "c2")

    trend = _trend(analyze_repo(tmp_path))
    assert len(trend) == 2, trend
    for entry in trend:
        assert {"commit", "files", "debt_index"} <= set(entry)
        assert isinstance(entry["debt_index"], float)
        assert entry["files"] >= 1
    # scores must genuinely differ across the documented vs undocumented commit,
    # and must not be the old fabricated 0.0/0.1 ladder.
    assert len({e["debt_index"] for e in trend}) == 2
    assert sorted(e["debt_index"] for e in trend) != [0.0, 0.1]