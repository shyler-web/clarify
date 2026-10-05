from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from paydown.config import load_signal_weights, load_thresholds
from paydown.repo import RepoAnalysis
from paydown.signals import (
    debt_index,
    signal_a_complexity,
    signal_b_size,
    signal_c_churn,
    signal_d_coupling,
    signal_e_intent,
    signal_f_provenance,
)


@dataclass
class FileScore:
    path: str
    score: float
    breakdown: dict[str, float] = field(default_factory=dict)


def rank_files(repo: RepoAnalysis) -> list[FileScore]:
    weights = load_signal_weights()
    thresholds = load_thresholds()
    churn = signal_c_churn(repo)
    coupling = signal_d_coupling(repo)

    ranked: list[FileScore] = []
    for f in repo.files:
        signals = {
            "cognitive_complexity": signal_a_complexity(f.source),
            "size_cyclomatic": signal_b_size(f.source),
            "churn": churn.get(f.path, 0.0),
            "coupling": coupling.get(f.path, 0.0),
            "intent_coverage": signal_e_intent(f.source),
            "ai_provenance": signal_f_provenance(f.source),
        }
        score = debt_index(signals, weights, thresholds, f.path)
        ranked.append(FileScore(path=Path(f.path), score=score, breakdown=signals))

    return sorted(ranked, key=lambda fs: fs.score, reverse=True)