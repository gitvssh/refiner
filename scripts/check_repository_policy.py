from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CI = ROOT / ".github/workflows/ci.yml"
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
UNTRUSTED_CI_TRIGGER = re.compile(r"(?m)^\s*pull_request(?:_target)?:\s*$")


def check_public_ci(problems: list[str]) -> None:
    if not PUBLIC_CI.is_file():
        problems.append("missing public CI workflow")
        return

    text = PUBLIC_CI.read_text(encoding="utf-8")
    if UNTRUSTED_CI_TRIGGER.search(text):
        problems.append("public CI must not execute fork pull requests on the internal runner")

    required = {
        "github.repository == 'gitvssh/refiner'": "repository identity guard",
        "github.actor == 'gitvssh'": "trusted actor guard",
        "runs-on: homelab-refiner": "dedicated ARC label",
        "permissions:\n  contents: read": "read-only workflow permissions",
    }
    for fragment, description in required.items():
        if fragment not in text:
            problems.append(f"public CI missing {description}")

    forbidden = {
        "runs-on: ubuntu-": "GitHub-hosted runner",
        "runs-on: windows-": "GitHub-hosted runner",
        "runs-on: macos-": "GitHub-hosted runner",
        "runs-on: self-hosted": "shared self-hosted runner label",
        "actions/cache@": "GitHub Actions cache storage",
        "actions/upload-artifact@": "GitHub Actions artifact storage",
        "actions/download-artifact@": "GitHub Actions artifact storage",
        "type=gha": "GitHub Actions BuildKit cache storage",
    }
    for fragment, description in forbidden.items():
        if fragment in text:
            problems.append(f"public CI uses forbidden {description}")


def main() -> int:
    problems: list[str] = []
    check_public_ci(problems)
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
