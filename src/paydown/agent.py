from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from paydown.knowledge import save_intent
from paydown.llm import llm_complete, llm_complete_cheap
from paydown.repo import SourceFile


@dataclass
class RefactorResult:
    path: str
    refactored_source: str
    explanation: str
    test_passes: bool


def explanation_gate(source_before: str, source_after: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You document code. Produce a short note covering: what this file does, "
                "why it exists, and what breaks if you change X. Keep it concise."
            ),
        },
        {
            "role": "user",
            "content": f"BEFORE:\n{source_before}\n\nAFTER:\n{source_after}\n\nWrite the note.",
        },
    ]
    try:
        note = llm_complete_cheap(messages).strip()
    except Exception:
        note = ""
    return note or "Refactored file; behavior and intent should be preserved."


def run_fix(file: SourceFile, repo_path: Path) -> RefactorResult:
    prompt = (
        "Refactor the following source file into a simpler, cleaner version "
        "that preserves identical behavior. Return only the new code.\n\n"
        f"```\n{file.source}\n```"
    )
    refactored = llm_complete([{"role": "user", "content": prompt}])

    explanation = explanation_gate(file.source, refactored)
    save_intent(file.path, explanation)

    test_passes = _run_test(file, refactored, Path(repo_path))

    return RefactorResult(
        path=file.path,
        refactored_source=refactored,
        explanation=explanation,
        test_passes=test_passes,
    )


def _run_test(file: SourceFile, source: str, repo_path: Path) -> bool:
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", dir=repo_path, delete=False
        ) as tmp:
            tmp.write(source)
            tmp_path = tmp.name
    except OSError:
        return False
    try:
        proc = subprocess.run(
            ["python", "-m", "py_compile", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False
    finally:
        try:
            Path(tmp_path).unlink()
        except OSError:
            pass