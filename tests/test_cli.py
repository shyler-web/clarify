def test_cli_help_prints_usage(capsys):
    from paydown.cli import main
    try:
        main(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "paydown" in out.lower()