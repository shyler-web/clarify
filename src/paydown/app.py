from __future__ import annotations

import io
import subprocess
import tarfile
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from paydown.agent import run_fix
from paydown.config import ConfigError, get_env
from paydown.knowledge import load_intent
from paydown.publish import open_pr
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


def _branch_slug(path: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in path).strip("-").lower()
    return slug[:60] or "fix"


def _trend(repo: RepoAnalysis) -> list[dict]:
    """Re-analyze the last N commits and compute the real debt score for each."""
    if not repo.files:
        return []
    root = repo.root
    try:
        commits = subprocess.run(
            ["git", "-C", str(root), "log", "--pretty=%h", "-n", "5"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        hashes = [h for h in commits.stdout.split() if h]
    except Exception:
        hashes = []
    trend: list[dict] = []
    for h in hashes:
        try:
            with tempfile.TemporaryDirectory() as td:
                arc = subprocess.run(
                    ["git", "-C", str(root), "archive", h], capture_output=True, timeout=30
                )
                if arc.returncode != 0:
                    continue
                with tarfile.open(fileobj=io.BytesIO(arc.stdout), mode="r:") as tf:
                    tf.extractall(td, filter="data")
                historical = analyze_repo(Path(td))
                if not historical.files:
                    continue
                scores = rank_files(historical)
                mean = sum(s.score for s in scores) / len(scores)
                trend.append(
                    {"commit": h, "files": len(historical.files), "debt_index": round(mean, 3)}
                )
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
        before = state.score_for(path)
        try:
            result = run_fix(source_file, state.root)
        except ConfigError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Missing configuration: {exc}",
            ) from exc

        target = Path(state.root) / result.path
        try:
            target.write_text(result.refactored_source, encoding="utf-8")
        except OSError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Could not write refactored file {result.path}: {exc}",
            ) from exc

        state.repo = analyze_repo(state.root)
        state.scores = rank_files(state.repo)
        state.files_by_path = {f.path: f for f in state.repo.files}
        after = state.score_for(path)
        result.before_score = before.score if before is not None else None
        result.after_score = after.score if after is not None else None

        entry = {
            "path": path,
            "status": "open",
            "explanation": result.explanation,
            "test_passes": result.test_passes,
        }
        if result.test_passes:
            try:
                repo_slug = get_env("GITHUB_REPO")
                branch = f"paydown/{_branch_slug(path)}"
                entry["url"] = open_pr(repo_slug, branch, result)
            except ConfigError as exc:
                entry["status"] = "skipped"
                entry["note"] = f"Publishing skipped: {exc}"
        state.prs.append(entry)
        return {
            "path": result.path,
            "explanation": result.explanation,
            "test_passes": result.test_passes,
            "refactored_source": result.refactored_source,
            "before_score": result.before_score,
            "after_score": result.after_score,
        }

    return app