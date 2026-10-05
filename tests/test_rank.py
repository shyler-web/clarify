def test_rank_files_descending(tmp_path):
    from pathlib import Path
    from paydown.rank import rank_files
    from paydown.repo import analyze_repo
    p = tmp_path / "r"
    p.mkdir()
    (p / "good.py").write_text("def f():\n    return 1\n")
    (p / "bad.py").write_text("def f():\n    if a:\n      for b in c:\n        if d:\n          pass\n")
    repo = analyze_repo(p)
    ranked = rank_files(repo)
    assert ranked[0].score >= ranked[-1].score
    assert ranked[0].path.endswith("bad.py")