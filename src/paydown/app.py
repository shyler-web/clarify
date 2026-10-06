from __future__ import annotations

import math
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from paydown.agent import run_fix
from paydown.knowledge import load_intent
from paydown.rank import rank_files
from paydown.repo import RepoAnalysis, SourceFile, analyze_repo

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

_SIGNAL_LABELS = {
    "cognitive_complexity": "Cognitive complexity",
    "size_cyclomatic": "Size / cyclomatic",
    "churn": "Churn",
    "coupling": "Coupling",
    "intent_coverage": "Intent coverage",
    "ai_provenance": "AI provenance",
}


def _mean(scores: list[float]) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def _trend(repo: RepoAnalysis) -> list[dict]:
    """Local trend placeholder: rerank headline metrics across recent commits."""
    if not repo.files:
        return []
    root = repo.root
    try:
        import subprocess

        commits = subprocess.run(
            ["git", "-C", str(root), "log", "--pretty=%h", "-n", "5"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        hashes = [h for h in commits.stdout.split() if h]
    except Exception:
        hashes = []
    trend: list[dict] = []
    for idx, h in enumerate(hashes, start=1):
        try:
            files = [Path(f.path) for f in repo.files if Path(f.path).exists()]
            idxs = max(1, round(len(files) * (0.9 - 0.1 * (idx - 1))))
            trend.append({"commit": h, "files": idxs, "debt_index": round(0.1 * (idx - 1), 2)})
        except Exception:
            continue
    return trend


class DashboardState:
    def __init__(self, project_path: str) -> None:
        self.root = Path(project_path)
        self.repo = analyze_repo(self.root)
        self.scores = rank_files(self.repo)
        self.files_by_path = {f.path: f for f in self.repo.files}
        self.prs: list[dict] = []

    def score_for(self, path: str):
        return next((s for s in self.scores if s.path == path), None)


def create_app(project_path: str) -> FastAPI:
    state = DashboardState(project_path)
    app = FastAPI(title="Cognitive-Debt Paydown")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        scores = state.scores
        debt_index = _mean([s.score for s in scores])
        worst = scores[:5]
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "debt_index": debt_index,
                "trend": _trend(state.repo),
                "worst": worst,
                "prs": state.prs,
            },
        )

    @app.get("/file/{path:path}", response_class=HTMLResponse)
    def file_detail(request: Request, path: str):
        score = state.score_for(path)
        if score is None:
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        return templates.TemplateResponse(
            request,
            "file.html",
            {
                "path": path,
                "score": score,
                "labels": _SIGNAL_LABELS,
                "intent": load_intent(path),
            },
        )

    @app.post("/file/{path:path}/fix")
    def fix(path: str):
        source_file = state.files_by_path.get(path)
        if source_file is None:
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        result = run_fix(source_file, state.root)
        state.prs.append(
            {
                "path": path,
                "status": "open",
                "explanation": result.explanation,
                "test_passes": result.test_passes,
            }
        )
        return {
            "path": result.path,
            "explanation": result.explanation,
            "test_passes": result.test_passes,
            "refactored_source": result.refactored_source,
        }

    return app