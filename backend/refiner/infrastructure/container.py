from __future__ import annotations

from dataclasses import dataclass

from refiner.application.usecases import ExportPdf, RefineResume
from refiner.application.workflows import RefinementWorkflow
from refiner.infrastructure.adapters import (
    DeterministicAnalyzer,
    MemoryExportGrantStore,
    MinimalPdfRenderer,
)


@dataclass(frozen=True, slots=True)
class Container:
    refine_resume: RefineResume
    export_pdf: ExportPdf
    grants: MemoryExportGrantStore


def build_container(*, export_ttl_seconds: int = 15 * 60) -> Container:
    analyzer = DeterministicAnalyzer()
    grants = MemoryExportGrantStore(ttl_seconds=export_ttl_seconds)
    workflow = RefinementWorkflow(analyzer)
    return Container(
        refine_resume=RefineResume(workflow, grants),
        export_pdf=ExportPdf(grants, MinimalPdfRenderer()),
        grants=grants,
    )
