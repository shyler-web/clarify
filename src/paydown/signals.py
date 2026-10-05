"""Debt Index signal computation for the Cognitive-Debt Paydown Agent.

Signals A, B, E, F are pure-code signals and return a single float from
``(src, language)`` input.  Signals C (churn) and D (coupling) are repo-level
and return ``dict[str, float]`` keyed by file path.
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

from radon.complexity import cc_visit

from paydown.repo import RepoAnalysis, analyze_repo

_COGNITIVE_KEYWORDS = (
    "if ", "for ", "while ", "catch ", "except ", "case ", "elif ",
    "else:", "switch ", "&&", "||",
)

_COMMENT_MARKERS = ("#", "//", "/*", "*", "--", "//!")


def _cognitive_count(src: str) -> int:
    """Crude cognitive-complexity proxy: keywords weighted by nesting depth."""
    depth = 0
    count = 0
    for raw in src.splitlines():
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip())
        if not stripped:
            continue
        if stripped.startswith(("}", ")", "]")):
            depth = max(0, indent - 1)
        if any(k in stripped for k in _COGNITIVE_KEYWORDS):
            count += 1 + depth
        depth = indent
    return count


def signal_a_complexity(src: str) -> float:
    """Cognitive complexity: radon cyclomatic + weighted nesting count (0-1)."""
    try:
        blocks = cc_visit(src)
        cc = max((b.complexity for b in blocks), default=1)
    except Exception:
        cc = 1
    cognitive = _cognitive_count(src)
    cc_norm = min(1.0, (cc - 1) / 9.0)
    cog_norm = min(1.0, cognitive / 10.0)
    return min(1.0, 0.5 * cc_norm + 0.5 * cog_norm)


def signal_b_size(src: str) -> float:
    """Size/cyclomatic: normalized function length + radon complexity (0-1)."""
    try:
        blocks = cc_visit(src)
    except Exception:
        blocks = []
    if not blocks:
        return 0.0
    max_len = 0
    for b in blocks:
        end = b.endline if b.endline else b.lineno
        max_len = max(max_len, end - b.lineno + 1)
    cc = max((b.complexity for b in blocks), default=1)
    len_norm = min(1.0, max_len / 50.0)
    cc_norm = min(1.0, (cc - 1) / 9.0)
    return min(1.0, 0.5 * len_norm + 0.5 * cc_norm)


def _git_changed_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "--format=", "--name-only"],
            cwd=str(root), capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return []
    return [line for line in out.stdout.splitlines() if line.strip()]


def _repo_age_days(root: Path) -> float:
    try:
        out = subprocess.run(
            ["git", "log", "--format=%ct", "--reverse"],
            cwd=str(root), capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return 1.0
    stamps = [int(t) for t in out.stdout.splitlines() if t.strip()]
    if not stamps:
        return 1.0
    return max(1.0, (stamps[-1] - stamps[0]) / 86400.0)


def signal_c_churn(repo: Path | str | RepoAnalysis) -> dict[str, float]:
    """Churn: commits touching a file per repo age, normalized (0-1)."""
    root = Path(repo) if isinstance(repo, (str, Path)) else Path(".")
    paths = [f.path for f in analyze_repo(root).files]
    changed = _git_changed_files(root)
    if not changed:
        return {p: 0.0 for p in paths}
    age_days = _repo_age_days(root)
    counts = Counter(changed)
    return {p: min(1.0, counts.get(p, 0) / age_days) for p in paths}


_LAYERED_NAMES = ("models", "domain", "entities", "services", "controllers", "api", "ui", "views")


def _layering_violations(path: str, deps: list[str]) -> int:
    low = path.lower()
    is_low_layer = any(f"/{name}/" in f"/{low}" or f"/{name}" in f"/{low}" or low.endswith(f"/{name}")
                        for name in ("models", "domain", "entities"))
    violations = 0
    for dep in deps:
        dl = dep.lower()
        if is_low_layer and any(f"/{name}/" in f"/{dl}" or f"/{name}" in f"/{dl}"
                                for name in ("controllers", "api", "ui", "views", "services")):
            violations += 1
    return violations


def signal_d_coupling(repo: RepoAnalysis | Path | str) -> dict[str, float]:
    """Coupling: incoming deps + layering violations, normalized per repo (0-1)."""
    if isinstance(repo, (str, Path)):
        repo = analyze_repo(Path(repo))
    total = max(1, len(repo.files))
    result: dict[str, float] = {}
    for f in repo.files:
        incoming = len(f.incoming_deps)
        layering = _layering_violations(f.path, f.incoming_deps)
        score = min(1.0, (incoming + layering) / (total * 0.5))
        result[f.path] = score
    return result


def signal_e_intent(src: str) -> float:
    """Intent coverage: fraction of functions with a docstring or comment (0-1)."""
    try:
        blocks = cc_visit(src)
    except Exception:
        blocks = []
    funcs = [b for b in blocks if b.is_method or b.__class__.__name__ == "Function"]
    if not funcs:
        return 0.0
    lines = src.splitlines()
    documented = 0
    for b in funcs:
        start = b.lineno - 1
        if start + 1 < len(lines):
            nxt = lines[start + 1].lstrip()
            if nxt.startswith(('"""', "'''")):
                documented += 1
                continue
        prev = lines[start - 1].strip() if start > 0 else ""
        if prev.startswith("#") or prev.startswith("//"):
            documented += 1
    return documented / len(funcs)


def signal_f_provenance(src: str) -> float:
    """AI-provenance heuristic: duplication + missing-comment ratio (0-1)."""
    nonempty = [line for line in src.splitlines() if line.strip()]
    if not nonempty:
        return 0.0
    code_lines = [
        line.strip()
        for line in nonempty
        if not any(line.strip().startswith(m) for m in _COMMENT_MARKERS)
    ]
    if not code_lines:
        return 0.0
    missing_comment = len(code_lines) / len(nonempty)
    counts = Counter(code_lines)
    duplicated = sum(c - 1 for c in counts.values() if c > 1)
    dup_ratio = min(1.0, duplicated / len(code_lines))
    return min(1.0, 0.5 * missing_comment + 0.5 * dup_ratio)


def _norm(value: float, thr: dict | None) -> float:
    """Map a 0-1 signal through thresholds; raw clamp when thresholds are empty."""
    if not thr:
        return min(1.0, max(0.0, value))
    high = thr.get("high")
    low = thr.get("low")
    if high is None or low is None or high <= low:
        return min(1.0, max(0.0, value))
    if value >= high:
        return 1.0
    if value <= low:
        return 0.0
    return (value - low) / (high - low)


def debt_index(
    signals: dict[str, float],
    weights: dict[str, float],
    thresholds: dict[str, dict] | None = None,
    file: str | None = None,
) -> float:
    """Weighted, normalized Debt Index score in [0, 100]."""
    thresholds = thresholds or {}
    total = 0.0
    for name, weight in weights.items():
        if name not in signals:
            continue
        thr = thresholds.get(name)
        total += weight * _norm(signals[name], thr)
    return 100.0 * total