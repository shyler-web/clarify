def test_cli_help_prints_usage(capsys):
    from paydown.cli import main
    try:
        main(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "paydown" in out.lower()


def test_cli_analyze_prints_clean_error_when_api_key_missing(tmp_path, monkeypatch, capsys):
    from paydown.cli import _cmd_analyze

    (tmp_path / "mod.py").write_text("def f():\n    return 1\n")
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    rc = _cmd_analyze(str(tmp_path))
    out = capsys.readouterr().out + capsys.readouterr().err
    assert rc != 0
    assert "NEBIUS_API_KEY" in out