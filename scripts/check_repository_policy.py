from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {".ai", ".claude", ".codex", ".git", "_vault"}
GENERATED_PARTS = {
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
FORBIDDEN_NAMES = {"AGENTS.md", "CLAUDE.md", "kubeconfig"}
FORBIDDEN_SUFFIXES = {".db", ".key", ".log", ".p12", ".pem", ".sqlite", ".sqlite3", ".tfstate"}
MEASUREMENT_ID = re.compile(r"\bG-[A-Z0-9]{8,}\b")


def main() -> int:
    problems: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in GENERATED_PARTS for part in relative.parts):
            continue
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            continue
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            problems.append(f"forbidden path: {relative}")
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        if MEASUREMENT_ID.search(text):
            problems.append(f"analytics measurement id in application code: {relative}")
    if problems:
        print("\n".join(problems))
        return 1
    print("Repository publication policy is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
