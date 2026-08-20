"""Pure resume-refinement rules with no framework or adapter dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass

MIN_RESUME_CHARACTERS = 40
MIN_JOB_DESCRIPTION_CHARACTERS = 40
MAX_TEXT_CHARACTERS = 20_000
TOKEN_PATTERN = re.compile(r"[^\W_]{2,}", re.UNICODE)
STOP_WORDS = frozenset(
    {
        "about",
        "an",
        "and",
        "are",
        "candidate",
        "candidates",
        "company",
        "driven",
        "experience",
        "fictional",
        "for",
        "from",
        "have",
        "hiring",
        "improve",
        "into",
        "is",
        "it",
        "its",
        "offs",
        "our",
        "requires",
        "role",
        "should",
        "supports",
        "that",
        "the",
        "this",
        "with",
        "you",
        "your",
    }
)
KEYWORD_ALIASES = {
    "designed": "design",
    "designing": "design",
    "engineers": "engineer",
    "metrics": "observability",
    "services": "service",
    "systems": "system",
    "tests": "test",
    "traces": "observability",
    "workflows": "workflow",
}


class RefinementValidationError(ValueError):
    """Raised when an input cannot safely enter the workflow."""


@dataclass(frozen=True, slots=True)
class RefinementAnalysis:
    coverage_score: int
    matched_keywords: tuple[str, ...]
    missing_keywords: tuple[str, ...]
    strengths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RefinementDraft:
    analysis: RefinementAnalysis
    rewritten_resume: str


def normalize_text(value: str, *, label: str) -> str:
    normalized = "\n".join(line.rstrip() for line in value.replace("\r\n", "\n").splitlines())
    normalized = normalized.strip()
    minimum = MIN_RESUME_CHARACTERS if label == "resume" else MIN_JOB_DESCRIPTION_CHARACTERS
    if len(normalized) < minimum:
        raise RefinementValidationError(f"{label} is too short for a useful refinement")
    if len(normalized) > MAX_TEXT_CHARACTERS:
        raise RefinementValidationError(
            f"{label} exceeds the {MAX_TEXT_CHARACTERS}-character limit"
        )
    if "\x00" in normalized:
        raise RefinementValidationError(f"{label} contains unsupported binary data")
    return normalized


def _keywords(value: str) -> set[str]:
    return {
        KEYWORD_ALIASES.get(match.group(0).casefold(), match.group(0).casefold())
        for match in TOKEN_PATTERN.finditer(value)
        if match.group(0).casefold() not in STOP_WORDS and not match.group(0).isdigit()
    }


def analyze_keyword_coverage(resume: str, job_description: str) -> RefinementAnalysis:
    resume_keywords = _keywords(resume)
    job_keywords = _keywords(job_description)
    matched = sorted(resume_keywords & job_keywords)
    missing = sorted(job_keywords - resume_keywords)
    denominator = max(len(job_keywords), 1)
    score = round(len(matched) / denominator * 100)

    strengths: list[str] = []
    if matched:
        strengths.append(f"Demonstrates {', '.join(matched[:5])} experience relevant to the role.")
    if any(character.isdigit() for character in resume):
        strengths.append("Includes quantified evidence that can support outcome-focused bullets.")
    if len(resume.splitlines()) >= 3:
        strengths.append("Provides enough structure to produce a concise role-focused draft.")
    if not strengths:
        strengths.append("Provides a usable baseline for a focused rewrite.")

    return RefinementAnalysis(
        coverage_score=score,
        matched_keywords=tuple(matched[:12]),
        missing_keywords=tuple(missing[:12]),
        strengths=tuple(strengths),
    )
