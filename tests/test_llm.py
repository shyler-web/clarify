import pytest


import pytest

from paydown import llm
from paydown.llm import ChatMessage


def test_llm_complete_requires_env(monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(Exception):
        llm.llm_complete([{"role": "user", "content": "hi"}])


def test_llm_complete_accepts_dict_and_chat_message(monkeypatch):
    captured = {}

    class FakeMessage:
        content = "reply"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    monkeypatch.setattr(llm, "_client", FakeClient())

    llm.llm_complete(
        [{"role": "user", "content": "hi"}, ChatMessage(role="assistant", content="hello")]
    )

    assert captured["messages"] == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]