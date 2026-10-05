import pytest


def test_llm_complete_requires_env(monkeypatch):
    from paydown import llm

    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(Exception):
        llm.llm_complete([{"role": "user", "content": "hi"}])