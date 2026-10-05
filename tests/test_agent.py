def test_run_fix_writes_explanation_and_does_not_publish_on_test_failure(tmp_path, monkeypatch):
    from paydown.agent import run_fix
    from paydown.repo import SourceFile
    monkeypatch.setenv("PAYDOWN_DB", str(tmp_path / "k.db"))
    # stub llm to produce a syntax-valid but behavior-breaking refactor
    def fake_complete(messages, model=""):
        return "# changed behavior incorrectly\ndef f():\n    return 99\n"
    monkeypatch.setattr("paydown.agent.llm_complete", fake_complete)
    sf = SourceFile(path="x.py", language="python", lines=2, source="def f():\n    return 1\n", imports=[], incoming_deps=[])
    res = run_fix(sf, repo_path=tmp_path)
    assert res.test_passes is False
    assert res.explanation  # explanation gate always written


def test_run_fix_passes_when_refactor_preserves_behavior(tmp_path, monkeypatch):
    from paydown.agent import run_fix
    from paydown.repo import SourceFile
    monkeypatch.setenv("PAYDOWN_DB", str(tmp_path / "k.db"))
    # stub llm to produce a refactor that preserves behavior
    def fake_complete(messages, model=""):
        return "# same behavior\ndef f():\n    return 1\n"
    monkeypatch.setattr("paydown.agent.llm_complete", fake_complete)
    sf = SourceFile(path="x.py", language="python", lines=2, source="def f():\n    return 1\n", imports=[], incoming_deps=[])
    res = run_fix(sf, repo_path=tmp_path)
    assert res.test_passes is True


def test_save_and_load_intent(tmp_path, monkeypatch):
    from paydown.knowledge import save_intent, load_intent
    monkeypatch.setenv("PAYDOWN_DB", str(tmp_path / "k.db"))
    save_intent("a.py", "note")
    assert load_intent("a.py") == "note"