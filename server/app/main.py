from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="EmeProbWriter",
    description="A multi-agent system for generating programming problems.",
    version="0.1.0",
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
