from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agents.algorithm_agent import algorithm_agent
from app.agents.content_agent import content_agent
from app.agents.requirement_agent import requirement_agent
from app.agents.solution_agent import solution_code_agent
from app.agents.supervisor import (
    ROUTE_HUMAN_REVIEW,
    ROUTE_PACKAGE,
    ROUTE_RETRY_SOLUTION,
    ROUTE_RETRY_TESTS,
    route_after_worker,
)
from app.agents.test_agent import test_generator_agent
from app.core.config import settings
from app.graph.state import AgentState
from app.worker.pipeline import WorkerError, run_worker_pipeline

_APPROVE_WORDS = {"yes", "y", "ok", "approve", "duyệt", "đồng ý"}

def _is_approved(feedback: str) -> bool:
    return str(feedback).strip().lower() in _APPROVE_WORDS


def _question(state: AgentState) -> str:
    return state["messages"][0].content

# Agent nodes

def requirement_node(state: AgentState):
    requirement = requirement_agent(_question(state))
    while True:
        feedback = interrupt(
            {
                "stage": "requirement",
                "message": "Review requirement: enter 'yes' or the content that needs to be revised.",
                "draft": requirement,
            }
        )
        if _is_approved(feedback):
            break
        requirement = requirement_agent(
            f"{_question(state)}\n\nFeedback from user:\n{feedback}"
        )
    return {
        "requirement": requirement,
        "requirement_approval": str(feedback),
        "checkpoint": feedback,
        "current_stage": "algorithm",
    }


def algorithm_node(state: AgentState):
    algorithm = algorithm_agent(_question(state), state["requirement"])
    while True:
        feedback = interrupt(
            {
                "stage": "algorithm",
                "message": "Enter 'yes' to approve the algorithm, or provide feedback for revision.",
                "draft": algorithm,
            }
        )
        if _is_approved(feedback):
            break
        algorithm = algorithm_agent(
            _question(state), state["requirement"], feedback=str(feedback)
        )
    return {
        "algorithm": algorithm,
        "algorithm_approval": str(feedback),
        "checkpoint": feedback,
        "current_stage": "content",
    }


def content_node(state: AgentState):
    content = content_agent(_question(state), state["requirement"], state["algorithm"])
    return {"content": content, "current_stage": "solution"}


def solution_node(state: AgentState):
    solution = solution_code_agent(
        state["content"],
        state["algorithm"],
        language=state.get("language", "python"),
        fix_feedback=state.get("worker_error") if state.get("worker_error_stage") == "solution" else None,
    )
    return {
        "solution_code": solution,
        "current_stage": "tests",
        "worker_error": None,
        "worker_error_stage": None,
    }


def tests_node(state: AgentState):
    tests_code = test_generator_agent(
        state["content"],
        state["solution_code"],
        fix_feedback=state.get("worker_error") if state.get("worker_error_stage") == "generator" else None,
    )
    return {
        "tests_generator_code": tests_code,
        "current_stage": "worker",
        "worker_error": None,
        "worker_error_stage": None,
    }


# Worker node

def worker_node(state: AgentState, config):
    thread_id = config["configurable"]["thread_id"]
    try:
        result = run_worker_pipeline(
            thread_id=thread_id,
            language=state.get("language", "python"),
            solution_raw=state["solution_code"],
            generator_raw=state["tests_generator_code"],
            content_md=state["content"],
            test_count=state.get("test_count", settings.default_test_count),
            sessions_dir=Path(settings.sessions_dir),
        )
        return {
            "worker_error": None,
            "worker_error_stage": None,
            "zip_path": result.zip_path,
            "tests_summary": result.tests_summary,
            "current_stage": "packaged",
        }
    except WorkerError as exc:
        return {
            "worker_error": str(exc),
            "worker_error_stage": exc.stage,
            "current_stage": "worker_failed",
        }

# Supervisor

def supervisor_node(state: AgentState):
    return {"fix_attempts": state.get("fix_attempts", 0) + 1}


def human_review_node(state: AgentState):
    decision = interrupt(
        {
            "stage": "human_review",
            "message": (
                "Worker has tried multiple times but failed. "
                "Enter 'retry' to try again from the beginning (reset attempt count), or 'abort' to stop."
            ),
            "error": state.get("worker_error"),
            "error_stage": state.get("worker_error_stage"),
        }
    )
    if str(decision).strip().lower() == "retry":
        return {"fix_attempts": 0, "current_stage": "solution"}
    return {"current_stage": "aborted"}


def _route_human_review(state: AgentState) -> str:
    return "solution" if state.get("current_stage") == "solution" else END


def build_graph(memory : any = InMemorySaver()) -> StateGraph:
    builder = StateGraph(AgentState)
    builder.add_node("requirement", requirement_node)
    builder.add_node("algorithm", algorithm_node)
    builder.add_node("content", content_node)
    builder.add_node("solution", solution_node)
    builder.add_node("tests", tests_node)
    builder.add_node("worker", worker_node)
    builder.add_node("supervisor_retry_solution", supervisor_node)
    builder.add_node("supervisor_retry_tests", supervisor_node)
    builder.add_node("human_review", human_review_node)

    builder.add_edge(START, "requirement")
    builder.add_edge("requirement", "algorithm")
    builder.add_edge("algorithm", "content")
    builder.add_edge("content", "solution")
    builder.add_edge("solution", "tests")
    builder.add_edge("tests", "worker")

    builder.add_conditional_edges(
        "worker",
        route_after_worker,
        {
            ROUTE_PACKAGE: END,
            ROUTE_RETRY_SOLUTION: "supervisor_retry_solution",
            ROUTE_RETRY_TESTS: "supervisor_retry_tests",
            ROUTE_HUMAN_REVIEW: "human_review",
        },
    )
    builder.add_edge("supervisor_retry_solution", "solution")
    builder.add_edge("supervisor_retry_tests", "tests")

    builder.add_conditional_edges(
        "human_review",
        _route_human_review,
        {"solution": "solution", END: END},
    )

    return builder.compile(checkpointer=memory)
