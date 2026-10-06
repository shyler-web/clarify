def test_lookup_docs_requires_env(monkeypatch):
    from paydown import tavily
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    try:
        tavily.lookup_docs("python 3.13 syntax")
        assert False, "should have raised"
    except Exception:
        pass