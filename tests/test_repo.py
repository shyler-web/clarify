def test_analyze_repo_skips_non_parseable_and_lists_files(tmp_path):
    from paydown.repo import analyze_repo
    p = tmp_path / "proj"
    p.mkdir(parents=True)
    (p / "a.py").write_text("def f():\n    return 1\n")
    (p / "b.txt").write_text("just text")
    (p / "broken.py").write_text("def (\n")  # unparseable
    res = analyze_repo(p)
    langs = {f.language for f in res.files}
    assert "python" in langs
    assert len(res.files) == 1  # broken.py skipped, b.txt not a code file


def test_analyze_repo_computes_imports_and_incoming_deps(tmp_path):
    from pathlib import Path
    from paydown.repo import analyze_repo
    p = tmp_path / "proj"
    p.mkdir(parents=True)
    (p / "a.py").write_text("def f():\n    return 1\n")
    (p / "b.py").write_text("from a import f\n")
    res = analyze_repo(p)
    by_stem = {Path(f.path).stem: f for f in res.files}
    assert by_stem["b"].imports
    assert str(by_stem["b"].path) in by_stem["a"].incoming_deps