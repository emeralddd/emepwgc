from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Raw idea from user")
    language: Literal["python", "cpp"] = "python"
    test_count: int = Field(default=20, ge=1, le=200)


class ResumeRequest(BaseModel):
    feedback: str = Field(..., description="'yes' to approve, or any other text to provide feedback for the worker.")


class SessionResponse(BaseModel):
    thread_id: str
    status: Literal["waiting_human", "done", "aborted", "running"]
    stage: Optional[str] = None
    checkpoint: Optional[Any] = None
    result: Optional[dict] = None
