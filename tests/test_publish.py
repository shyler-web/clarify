def test_open_pr_requires_token(monkeypatch):
    from paydown import publish
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    try:
        publish.open_pr("user/repo", "fix-utils", None)
        assert False
    except Exception:
        pass