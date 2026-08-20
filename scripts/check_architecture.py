from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "backend/refiner"

FORBIDDEN_IMPORTS = {
    "core": ("refiner.application", "refiner.infrastructure", "fastapi"),
    "application": ("refiner.infrastructure", "refiner.interfaces", "fastapi"),
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def violations() -> list[str]:
    problems: list[str] = []
    for layer, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
        for path in sorted((PACKAGE / layer).rglob("*.py")):
            for module in imported_modules(path):
                if module.startswith(forbidden_prefixes):
                    relative = path.relative_to(ROOT)
                    problems.append(f"{relative}: forbidden dependency {module}")
    return problems


def main() -> int:
    problems = violations()
    if problems:
        print("\n".join(problems))
        return 1
    print("Architecture dependency direction is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
