from refiner.core.domain.refinement import (
    RefinementValidationError,
    analyze_keyword_coverage,
    normalize_text,
)


def test_keyword_analysis_is_deterministic() -> None:
    resume = "Built reliable Python APIs with FastAPI and PostgreSQL for 2 million payment events."
    job = "We need Python FastAPI PostgreSQL Kubernetes observability and payment experience."

    analysis = analyze_keyword_coverage(resume, job)

    assert 0 < analysis.coverage_score < 100
    assert {"python", "fastapi", "postgresql", "payment"}.issubset(analysis.matched_keywords)
    assert "kubernetes" in analysis.missing_keywords
    assert any("quantified" in strength for strength in analysis.strengths)


def test_normalize_text_enforces_bounds() -> None:
    try:
        normalize_text("too short", label="resume")
    except RefinementValidationError as exc:
        assert "too short" in str(exc)
    else:
        raise AssertionError("short input must be rejected")
