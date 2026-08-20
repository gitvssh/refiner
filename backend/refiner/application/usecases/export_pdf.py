from __future__ import annotations

from refiner.core.ports import ExportGrantStorePort, PdfRendererPort


class ExportPdf:
    def __init__(self, grants: ExportGrantStorePort, renderer: PdfRendererPort) -> None:
        self._grants = grants
        self._renderer = renderer

    def execute(self, token: str) -> bytes:
        rewritten_resume = self._grants.consume(token)
        return self._renderer.render(rewritten_resume)
