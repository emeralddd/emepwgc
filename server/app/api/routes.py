import sqlite3
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.build_graph import build_graph
from app.schemas.models import CreateSessionRequest, ResumeRequest, SessionResponse

router = APIRouter()

conn = sqlite3.connect("database/checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

_graph_app = build_graph(memory=memory) 


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _snapshot_to_response(thread_id: str) -> SessionResponse:
    snapshot = _graph_app.get_state(_config(thread_id))
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Cannot find session.")

    if snapshot.next:
        payload = None
        for task in snapshot.tasks:
            if task.interrupts:
                payload = task.interrupts[0].value
                break
        return SessionResponse(
            thread_id=thread_id,
            status="waiting_human",
            stage=(payload or {}).get("stage", snapshot.values.get("current_stage")),
            checkpoint=payload,
        )

    stage = snapshot.values.get("current_stage")
    if stage == "aborted":
        return SessionResponse(thread_id=thread_id, status="aborted", stage=stage)

    return SessionResponse(
        thread_id=thread_id,
        status="done",
        stage=stage,
        result={
            "content": snapshot.values.get("content"),
            "solution_code": snapshot.values.get("solution_code"),
            "tests_summary": snapshot.values.get("tests_summary"),
            "zip_path": snapshot.values.get("zip_path"),
        },
    )


@router.post("/sessions", response_model=SessionResponse)
def create_session(req: CreateSessionRequest):
    thread_id = str(uuid.uuid4())
    initial_state = {
        "messages": [{"role": "user", "content": req.question}],
        "language": req.language,
        "test_count": req.test_count,
        "fix_attempts": 0,
    }
    _graph_app.invoke(initial_state, _config(thread_id))
    return _snapshot_to_response(thread_id)


@router.post("/sessions/{thread_id}/resume", response_model=SessionResponse)
def resume_session(thread_id: str, req: ResumeRequest):
    snapshot = _graph_app.get_state(_config(thread_id))
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Cannot find session.")
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="Session was finished.")

    _graph_app.invoke(Command(resume=req.feedback), _config(thread_id))
    return _snapshot_to_response(thread_id)


@router.get("/sessions/{thread_id}", response_model=SessionResponse)
def get_session(thread_id: str):
    return _snapshot_to_response(thread_id)


@router.get("/sessions/{thread_id}/download")
def download_zip(thread_id: str):
    snapshot = _graph_app.get_state(_config(thread_id))
    zip_path = snapshot.values.get("zip_path") if snapshot.values else None
    if not zip_path or not Path(zip_path).exists():
        raise HTTPException(status_code=404, detail="Cannot find zip file (problem not completed).")
    return FileResponse(zip_path, filename="problem.zip", media_type="application/zip")
