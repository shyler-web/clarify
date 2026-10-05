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


_HARNESS = (
    "import sys\n"
    "src_path = sys.argv[1]\n"
    "ns = {}\n"
    "with open(src_path) as _f:\n"
    "    exec(compile(_f.read(), src_path, 'exec'), ns)\n"
    "out = []\n"
    "for _name, _val in sorted(ns.items()):\n"
    "    if _name.startswith('_'):\n"
    "        continue\n"
    "    if callable(_val) and not isinstance(_val, type):\n"
    "        try:\n"
    "            out.append('%s=%r' % (_name, _val()))\n"
    "        except TypeError:\n"
    "            pass\n"
    "print(';'.join(out))\n"
)


def _write_temp(repo_path: Path, suffix: str, content: str) -> Path | None:
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, dir=repo_path, delete=False
        ) as tmp:
            tmp.write(content)
            return Path(tmp.name)
    except OSError:
        return None


def _run_process(cmd: list[str]) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError):
        return None


def _behavior_signal(source: str, repo_path: Path) -> str | None:
    harness = _write_temp(repo_path, ".py", _HARNESS)
    mod = _write_temp(repo_path, ".py", source)
    if harness is None or mod is None:
        if harness:
            harness.unlink()
        if mod:
            mod.unlink()
        return None
    try:
        proc = _run_process(["python", str(harness), str(mod)])
        return proc.stdout if proc is not None and proc.returncode == 0 else None
    finally:
        try:
            harness.unlink()
        except OSError:
            pass
        try:
            mod.unlink()
        except OSError:
            pass


def _run_test(file: SourceFile, source: str, repo_path: Path) -> bool:
    before = _behavior_signal(file.source, repo_path)
    after = _behavior_signal(source, repo_path)
    if before is None or after is None:
        return False
    return before == after