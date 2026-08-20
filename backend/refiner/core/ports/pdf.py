from __future__ import annotations

from typing import Protocol


class PdfRendererPort(Protocol):
    def render(self, rewritten_resume: str) -> bytes: ...
