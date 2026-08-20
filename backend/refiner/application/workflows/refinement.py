"""Explicit workflow state and thin nodes for the complex refinement path."""

from __future__ import annotations

from dataclasses import dataclass

from refiner.core.domain import RefinementAnalysis, RefinementDraft, normalize_text
from refiner.core.ports import AnalyzerPort


@dataclass(slots=True)
class RefinementState:
    resume: str
    job_description: str
    analysis: RefinementAnalysis | None = None
    rewritten_resume: str | None = None


def validate_inputs(state: RefinementState) -> None:
    state.resume = normalize_text(state.resume, label="resume")
    state.job_description = normalize_text(state.job_description, label="job description")


def analyze_resume(state: RefinementState, analyzer: AnalyzerPort) -> None:
    state.analysis = analyzer.analyze(state.resume, state.job_description)


def rewrite_resume(state: RefinementState, analyzer: AnalyzerPort) -> None:
    if state.analysis is None:
        raise RuntimeError("analysis node must run before rewrite node")
    state.rewritten_resume = analyzer.rewrite(state.resume, state.analysis)


class RefinementWorkflow:
    def __init__(self, analyzer: AnalyzerPort) -> None:
        self._analyzer = analyzer

    def run(self, resume: str, job_description: str) -> RefinementDraft:
        state = RefinementState(resume=resume, job_description=job_description)
        validate_inputs(state)
        analyze_resume(state, self._analyzer)
        rewrite_resume(state, self._analyzer)
        if state.analysis is None or state.rewritten_resume is None:
            raise RuntimeError("refinement workflow completed without a result")
        return RefinementDraft(
            analysis=state.analysis,
            rewritten_resume=state.rewritten_resume,
        )
