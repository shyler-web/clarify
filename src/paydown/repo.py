from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from tree_sitter import Language, Parser

try:
    import tree_sitter_python
    _PY_LANG = Language(tree_sitter_python.language())
except Exception:  # pragma: no cover - grammar not installed
    _PY_LANG = None

_CODE_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
}

# Heuristic fallbacks for languages without a bundled grammar.
_IMPORT_PATTERNS: dict[str, list[re.Pattern]] = {
    "javascript": [re.compile(r"(?:require\s*\(\s*|import\s+)(['\"])([^'\"]+)\1")],
    "typescript": [re.compile(r"(?:require\s*\(\s*|import\s+)(['\"])([^'\"]+)\1")],
    "go": [re.compile(r"\bimport\s+(?:\([^)]*\)|[^\n]+)")],
    "rust": [re.compile(r"\buse\s+([\w:]+)")],
    "java": [re.compile(r"\bimport\s+([\w.]+)")],
    "cpp": [re.compile(r"#\s*include\s*[<\"]([^>\"]+)")],
    "c": [re.compile(r"#\s*include\s*[<\"]([^>\"]+)")],
}

_PY_IMPORT_NODES = {"import_statement", "import_from_statement", "future_import_statement"}


@dataclass
class SourceFile:
    path: str
    language: str
    lines: int
    source: str
    imports: list[str] = field(default_factory=list)
    incoming_deps: list[str] = field(default_factory=list)


@dataclass
class RepoAnalysis:
    files: list[SourceFile] = field(default_factory=list)


def _extract_python_imports(node) -> list[str]:
    imports: list[str] = []
    stack = [node]
    while stack:
        cur = stack.pop()
        if cur.type in _PY_IMPORT_NODES:
            imports.append(cur.text.decode("utf-8"))
            continue
        stack.extend(cur.children)
    return imports


def _extract_imports(source: str, language: str) -> list[str]:
    patterns = _IMPORT_PATTERNS.get(language, [])
    found: list[str] = []
    for pat in patterns:
        found.extend(m.group(0).strip() for m in pat.finditer(source))
    return found


def _parse_file(path: Path, language: str) -> SourceFile | None:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None
    if language == "python":
        try:
            parser = Parser(_PY_LANG)
            tree = parser.parse(source.encode("utf-8"))
            if tree.root_node.has_error:
                return None  # unparseable -> skip
            imports = _extract_python_imports(tree.root_node)
        except Exception:
            return None  # unparseable -> skip
    else:
        imports = _extract_imports(source, language)
    return SourceFile(
        path=str(path),
        language=language,
        lines=source.count("\n") + 1,
        source=source,
        imports=imports,
    )


def analyze_repo(path: Path) -> RepoAnalysis:
    root = Path(path)
    analysis = RepoAnalysis()
    if not root.is_dir():
        return analysis
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        language = _CODE_EXTENSIONS.get(file_path.suffix.lower())
        if language is None:
            continue
        sf = _parse_file(file_path, language)
        if sf is not None:
            analysis.files.append(sf)
    _compute_incoming_deps(analysis)
    return analysis


def _normalize_import(imp: str) -> str:
    imp = imp.strip()
    if imp.startswith("from "):
        m = re.match(r"^from\s+(\w+(?:\.\w+)*)\s+import\b", imp)
        if m:
            imp = m.group(1)
        return imp
    imp = re.sub(r"^import\s+", "", imp)
    imp = re.sub(r"^#\s*include\s*[<\"']", "", imp)
    imp = re.sub(r"^use\s+", "", imp)
    imp = imp.strip()
    for sep in ("\n", "(", ",", ";", " as ", "::", "."):
        imp = imp.split(sep)[0]
    imp = re.sub(r"[\"';,)]", "", imp).strip()
    return imp


def _module_targets(imp: str) -> list[str]:
    norm = _normalize_import(imp)
    candidates = [norm]
    parts = norm.split(".")
    if len(parts) > 1:
        candidates.append(parts[0])
    return [c for c in candidates if c]


def _compute_incoming_deps(analysis: RepoAnalysis) -> None:
    stems = {Path(f.path).stem: f for f in analysis.files}
    for f in analysis.files:
        incoming: set[str] = set()
        for other in analysis.files:
            if other is f:
                continue
            for imp in other.imports:
                for target in _module_targets(imp):
                    hit = stems.get(target)
                    if hit is not None and hit is f:
                        incoming.add(str(other.path))
        f.incoming_deps = sorted(incoming)