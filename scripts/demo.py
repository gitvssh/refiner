from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, cast

from fastapi.testclient import TestClient
from refiner.interfaces.api.app import create_app

ROOT = Path(__file__).resolve().parents[1]


def run_demo() -> Path:
    resume = (ROOT / "examples/sample-resume.txt").read_bytes()
    job_description = (ROOT / "examples/job-description.txt").read_text(encoding="utf-8")
    with TestClient(create_app()) as client:
        refinement = client.post(
            "/api/v1/refinements",
            files={"resume": ("sample-resume.txt", resume, "text/plain")},
            data={"job_description": job_description},
        )
        refinement.raise_for_status()
        payload = cast(dict[str, Any], refinement.json())
        exported = client.post(
            "/api/v1/exports/pdf",
            headers={"X-Export-Token": str(payload["export_token"])},
        )
        exported.raise_for_status()

    destination = Path(tempfile.gettempdir()) / "refiner-synthetic-demo.pdf"
    destination.write_bytes(exported.content)
    print(
        "Synthetic refinement complete: "
        f"coverage={payload['analysis']['coverage_score']}%, pdf={destination}"
    )
    return destination


if __name__ == "__main__":
    run_demo()
