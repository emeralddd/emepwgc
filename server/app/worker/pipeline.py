from dataclasses import dataclass
from pathlib import Path

from app.worker.code_extractor import CodeExtractionError, extract_code
from app.worker.executor import CompileError, RuntimeExecError, prepare_runnable
from app.worker.packager import package_problem
from app.worker.test_runner import GeneratorError, build_test_cases, write_test_files


class WorkerError(Exception):
    def __init__(self, message: str, stage: str):
        super().__init__(message)
        self.stage = stage  # solution || generator


@dataclass
class WorkerResult:
    zip_path: str
    tests_summary: str


def run_worker_pipeline(
    thread_id: str,
    language: str,
    solution_raw: str,
    generator_raw: str,
    content_md: str,
    test_count: int,
    sessions_dir: Path,
) -> WorkerResult:
    session_dir = sessions_dir / thread_id
    build_dir = session_dir / "build"
    tests_dir = session_dir / "tests"
    zip_path = session_dir / "problem.zip"

    # Get output code from agent's raw output.
    try:
        solution_code = extract_code(solution_raw, language)
    except CodeExtractionError as exc:
        raise WorkerError(str(exc), stage="solution") from exc

    try:
        generator_code = extract_code(generator_raw, "python")
    except CodeExtractionError as exc:
        raise WorkerError(str(exc), stage="generator") from exc

    # Compile solution code (if C++) and prepare runnable.
    try:
        runnable = prepare_runnable(language, solution_code, build_dir)
    except CompileError as exc:
        raise WorkerError(f"Compile solution failed:\n{exc}", stage="solution") from exc

    # Run test generator to produce test cases, and write them to files.
    try:
        cases = build_test_cases(generator_code, runnable, build_dir, count=test_count)
    except GeneratorError as exc:
        raise WorkerError(str(exc), stage="generator") from exc
    except RuntimeExecError as exc:
        raise WorkerError(f"Solution failed when running with generated tests:\n{exc}", stage="solution") from exc

    if not cases:
        raise WorkerError("No test cases generated.", stage="generator")

    write_test_files(cases, tests_dir)

    # Package zip.
    package_problem(
        problem_dir=session_dir / "package",
        content_md=content_md,
        solution_code=solution_code,
        language=language,
        tests_dir=tests_dir,
        zip_path=zip_path,
    )

    summary = f"Generated {len(cases)} test cases, packaged at {zip_path}."
    return WorkerResult(zip_path=str(zip_path), tests_summary=summary)
