from __future__ import annotations

import re

from refiner.core.domain import RefinementAnalysis, analyze_keyword_coverage


class DeterministicAnalyzer:
    """An offline adapter that keeps the public demo repeatable and credential-free."""

    def analyze(self, resume: str, job_description: str) -> RefinementAnalysis:
        return analyze_keyword_coverage(resume, job_description)

    def rewrite(self, resume: str, analysis: RefinementAnalysis) -> str:
        candidate_lines = [
            re.sub(r"^[\s•*-]+", "", line).strip() for line in resume.splitlines() if line.strip()
        ]
        evidence = [line for line in candidate_lines if len(line) >= 18]
        if not evidence:
            evidence = candidate_lines

        output = ["ROLE-FOCUSED SUMMARY"]
        if analysis.matched_keywords:
            output.append("Relevant strengths: " + ", ".join(analysis.matched_keywords[:6]) + ".")
        else:
            output.append(
                "Relevant strengths: transferable delivery and problem-solving experience."
            )
        output.extend(("", "SELECTED EVIDENCE"))
        output.extend(f"- {line.rstrip('.')}" + "." for line in evidence[:6])
        if analysis.missing_keywords:
            output.extend(
                (
                    "",
                    "REVIEW BEFORE APPLYING",
                    "Only add these role terms when supported by real experience: "
                    + ", ".join(analysis.missing_keywords[:6])
                    + ".",
                )
            )
        return "\n".join(output)
