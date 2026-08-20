from __future__ import annotations

from typing import Protocol

from refiner.core.domain import RefinementAnalysis


class AnalyzerPort(Protocol):
    def analyze(self, resume: str, job_description: str) -> RefinementAnalysis: ...

    def rewrite(self, resume: str, analysis: RefinementAnalysis) -> str: ...
