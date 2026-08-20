from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PHASES = ("quickstart", "lint", "typecheck", "test", "audit", "sbom", "license")


def run(argv: Sequence[str], *, cwd: Path = ROOT, capture: bool = False) -> str:
    print("+", " ".join(argv))
    result = subprocess.run(
        list(argv),
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        if capture:
            print("Command failed; output was intentionally withheld.", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout if capture else ""


def quickstart() -> None:
    run(["uv", "sync", "--frozen"])
    run(["npm", "ci"], cwd=FRONTEND)
    run(["uv", "run", "python", "scripts/check_repository_policy.py"])
    run(["uv", "run", "python", "scripts/demo.py"])


def lint() -> None:
    run(["uv", "run", "ruff", "check", "."])
    run(["uv", "run", "ruff", "format", "--check", "."])
    run(["uv", "run", "python", "scripts/check_architecture.py"])
    run(["npm", "run", "lint"], cwd=FRONTEND)


def typecheck() -> None:
    run(["uv", "run", "mypy"])
    run(["npm", "run", "typecheck"], cwd=FRONTEND)


def test() -> None:
    run(["uv", "run", "pytest"])
    run(["npm", "run", "test"], cwd=FRONTEND)
    run(["npm", "run", "build"], cwd=FRONTEND)


def audit() -> None:
    with tempfile.NamedTemporaryFile(prefix="refiner-requirements-", suffix=".txt") as exported:
        run(
            [
                "uv",
                "export",
                "--quiet",
                "--frozen",
                "--no-emit-project",
                "--no-hashes",
                "--output-file",
                exported.name,
            ]
        )
        run(["uv", "run", "pip-audit", "--strict", "--requirement", exported.name])
    run(["npm", "audit", "--omit=dev", "--audit-level=high"], cwd=FRONTEND)


def sbom() -> None:
    with tempfile.TemporaryDirectory(prefix="refiner-sbom-") as temporary:
        directory = Path(temporary)
        backend_path = directory / "backend.cdx.json"
        run(
            [
                "uv",
                "run",
                "cyclonedx-py",
                "environment",
                "--output-format",
                "JSON",
                "--output-file",
                str(backend_path),
            ]
        )
        backend_sbom = cast(dict[str, Any], json.loads(backend_path.read_text(encoding="utf-8")))
        frontend_raw = run(
            ["npm", "sbom", "--sbom-format", "cyclonedx"],
            cwd=FRONTEND,
            capture=True,
        )
        frontend_sbom = cast(dict[str, Any], json.loads(frontend_raw))
        for name, document in (("backend", backend_sbom), ("frontend", frontend_sbom)):
            if document.get("bomFormat") != "CycloneDX" or not document.get("components"):
                raise SystemExit(f"{name} SBOM is empty or invalid")
    print("Backend and frontend CycloneDX SBOMs are valid.")


def license_review() -> None:
    python_raw = run(["uv", "run", "pip-licenses", "--format=json"], capture=True)
    python_packages = cast(list[dict[str, Any]], json.loads(python_raw))
    lock = cast(
        dict[str, Any],
        json.loads((FRONTEND / "package-lock.json").read_text(encoding="utf-8")),
    )
    node_packages = cast(dict[str, dict[str, Any]], lock.get("packages", {}))
    licenses = [str(item.get("License", "")) for item in python_packages]
    licenses.extend(
        str(item.get("license", ""))
        for path, item in node_packages.items()
        if path and "node_modules/" in path
    )
    unknown = [
        license_name for license_name in licenses if not license_name or license_name == "UNKNOWN"
    ]
    forbidden = []
    for license_name in licenses:
        normalized = license_name.upper()
        strong_copyleft = (
            "AGPL" in normalized
            or "SSPL" in normalized
            or ("GPL" in normalized and "LGPL" not in normalized)
        )
        if strong_copyleft:
            forbidden.append(license_name)
    if unknown or forbidden:
        raise SystemExit(
            f"license review failed: unknown={len(unknown)}, forbidden={len(forbidden)}"
        )
    print(f"Dependency license review passed for {len(licenses)} package records.")


FUNCTIONS = {
    "quickstart": quickstart,
    "lint": lint,
    "typecheck": typecheck,
    "test": test,
    "audit": audit,
    "sbom": sbom,
    "license": license_review,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=(*PHASES, "all"))
    arguments = parser.parse_args()
    selected = PHASES if arguments.phase == "all" else (arguments.phase,)
    for phase in selected:
        print(f"== {phase} ==")
        FUNCTIONS[phase]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
