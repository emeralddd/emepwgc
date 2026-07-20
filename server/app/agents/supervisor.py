from app.core.config import settings
from app.graph.state import AgentState

ROUTE_PACKAGE = "package"
ROUTE_RETRY_SOLUTION = "retry_solution"
ROUTE_RETRY_TESTS = "retry_tests"
ROUTE_HUMAN_REVIEW = "human_review"


def route_after_worker(state: AgentState) -> str:
    if not state.get("worker_error"):
        return ROUTE_PACKAGE

    attempts = state.get("fix_attempts", 0)
    if attempts >= settings.max_solution_fix_attempts:
        return ROUTE_HUMAN_REVIEW

    stage = state.get("worker_error_stage")
    if stage == "generator":
        return ROUTE_RETRY_TESTS

    return ROUTE_RETRY_SOLUTION
