from typing import Any, Literal, Optional

from langgraph.graph import MessagesState

Language = Literal["python", "cpp"]


class AgentState(MessagesState):
    # User input
    language: Language
    test_count: int

    # Agent output
    requirement: str
    requirement_approval: str
    algorithm: str
    algorithm_approval: str
    content: str
    solution_code: str
    tests_generator_code: str

    # Checkpoint
    current_stage: str
    checkpoint: Any

    # Worker
    worker_error: Optional[str]
    worker_error_stage: Optional[str]  # solution || generator
    fix_attempts: int
    zip_path: Optional[str]
    tests_summary: Optional[str]
