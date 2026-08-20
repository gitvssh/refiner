from refiner.application.workflows import RefinementWorkflow
from refiner.infrastructure.adapters import DeterministicAnalyzer


def test_workflow_returns_reviewable_draft() -> None:
    workflow = RefinementWorkflow(DeterministicAnalyzer())
    result = workflow.run(
        "Built Python APIs for payment reconciliation and reduced duplicate work by 42 percent.",
        "The role needs Python APIs Kubernetes observability and reliable payment reconciliation.",
    )

    assert result.analysis.coverage_score > 0
    assert "ROLE-FOCUSED SUMMARY" in result.rewritten_resume
    assert "Only add these role terms" in result.rewritten_resume
