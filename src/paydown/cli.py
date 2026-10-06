from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paydown.agent import run_fix
from paydown.rank import rank_files
from paydown.repo import analyze_repo

_PROG = "paydown"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Cognitive-Debt Paydown: score a repo's files, pay down the worst debt.",
    )
    sub = parser.add_subparsers(dest="command")

    analyze = sub.add_parser(
        "analyze",
        help="Analyze a repo, print ranked files, and run a fix on the worst.",
    )
    analyze.add_argument("repo_path", help="Path to the repository to analyze.")

    serve = sub.add_parser(
        "serve",
        help="Start the FastAPI dashboard for a repo.",
    )
    serve.add_argument("repo_path", help="Path to the repository to serve.")
    serve.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    serve.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000).")

    return parser


def _ranked(repo_path: str) -> list:
    root = Path(repo_path)
    repo = analyze_repo(root)
    return rank_files(repo), repo


def _cmd_analyze(repo_path: str) -> int:
    scores, repo = _ranked(repo_path)
    if not scores:
        print(f"{_PROG}: no analyzable source files found in '{repo_path}'")
        return 1

    print(f"Debt Index ranking for {repo.root}:")
    for i, score in enumerate(scores, start=1):
        print(f"  {i:2d}. {score.score:6.2f}  {score.path}")

    worst = scores[0]
    source = next((f for f in repo.files if f.path == worst.path), None)
    if source is None:
        print(f"{_PROG}: could not load source for worst file '{worst.path}'")
        return 1

    print(f"\nRunning a fix on the worst file: {worst.path}")
    result = run_fix(source, repo.root)
    print(f"  test_passes: {result.test_passes}")
    print(f"  explanation: {result.explanation}")
    return 0


def _cmd_serve(repo_path: str, host: str, port: int) -> int:
    try:
        import uvicorn
    except ImportError:
        print(f"{_PROG}: 'uvicorn' is required for 'serve'. Run: uv add uvicorn")
        return 1
    from paydown.app import create_app

    app = create_app(project_path=repo_path)
    uvicorn.run(app, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        sys.exit(_cmd_analyze(args.repo_path))
    if args.command == "serve":
        sys.exit(_cmd_serve(args.repo_path, args.host, args.port))
    parser.print_help()


if __name__ == "__main__":
    main()