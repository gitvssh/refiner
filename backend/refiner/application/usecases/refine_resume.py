from __future__ import annotations

from dataclasses import dataclass

from refiner.application.workflows import RefinementWorkflow
from refiner.core.domain import RefinementAnalysis, RefinementValidationError
from refiner.core.ports.export_grants import ExportGrantStorePort

MAX_UPLOAD_BYTES = 256 * 1024


class UploadValidationError(ValueError):
    """The uploaded resume is not a safe, supported text document."""


@dataclass(frozen=True, slots=True)
class RefinementResult:
    analysis: RefinementAnalysis
    rewritten_resume: str
    export_token: str
    export_expires_in_seconds: int


class RefineResume:
    def __init__(
        self,
        workflow: RefinementWorkflow,
        export_grants: ExportGrantStorePort,
    ) -> None:
        self._workflow = workflow
        self._export_grants = export_grants

    def execute(self, uploaded_bytes: bytes, job_description: str) -> RefinementResult:
        if not uploaded_bytes or len(uploaded_bytes) > MAX_UPLOAD_BYTES:
            raise UploadValidationError("resume must be a non-empty file smaller than 256 KiB")
        try:
            resume = uploaded_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UploadValidationError("resume must be UTF-8 plain text") from exc

        try:
            draft = self._workflow.run(resume, job_description)
        except RefinementValidationError as exc:
            raise UploadValidationError(str(exc)) from exc
        grant = self._export_grants.issue(draft.rewritten_resume)
        return RefinementResult(
            analysis=draft.analysis,
            rewritten_resume=draft.rewritten_resume,
            export_token=grant.token,
            export_expires_in_seconds=grant.expires_in_seconds,
        )
