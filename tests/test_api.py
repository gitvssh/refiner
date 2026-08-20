from pathlib import Path
from typing import Any, cast

from fastapi.testclient import TestClient
from refiner.infrastructure.container import build_container
from refiner.interfaces.api.app import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_complete_refine_and_single_use_export_flow() -> None:
    container = build_container(export_ttl_seconds=60)
    resume = (ROOT / "examples/sample-resume.txt").read_bytes()
    job = (ROOT / "examples/job-description.txt").read_text(encoding="utf-8")

    with TestClient(create_app(container)) as client:
        refinement = client.post(
            "/api/v1/refinements",
            files={"resume": ("sample-resume.txt", resume, "text/plain")},
            data={"job_description": job},
        )
        assert refinement.status_code == 201
        payload = cast(dict[str, Any], refinement.json())
        token = str(payload["export_token"])
        assert len(token) >= 32
        assert container.grants.active_count() == 1

        exported = client.post("/api/v1/exports/pdf", headers={"X-Export-Token": token})
        assert exported.status_code == 200
        assert exported.headers["content-type"] == "application/pdf"
        assert exported.content.startswith(b"%PDF-1.4")
        assert exported.content.endswith(b"%%EOF\n")
        assert container.grants.active_count() == 0

        repeated = client.post("/api/v1/exports/pdf", headers={"X-Export-Token": token})
        assert repeated.status_code == 404


def test_rejects_unsupported_or_binary_uploads() -> None:
    with TestClient(create_app()) as client:
        wrong_suffix = client.post(
            "/api/v1/refinements",
            files={"resume": ("resume.pdf", b"not a PDF", "application/pdf")},
            data={"job_description": "A sufficiently long synthetic role description for testing."},
        )
        assert wrong_suffix.status_code == 415

        binary = client.post(
            "/api/v1/refinements",
            files={"resume": ("resume.txt", b"\xff" * 80, "text/plain")},
            data={"job_description": "A sufficiently long synthetic role description for testing."},
        )
        assert binary.status_code == 422
