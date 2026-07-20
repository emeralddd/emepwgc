import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings
from app.worker.executor import Runnable, RuntimeExecError, run_with_input


class GeneratorError(Exception):
    pass


@dataclass
class TestCase:
    index: int
    input_text: str
    output_text: str


def _run_generator(generator_path: Path, seed: int) -> str:
    try:
        proc = subprocess.run(
            ["python3", str(generator_path), str(seed)],
            capture_output=True,
            text=True,
            timeout=settings.exec_timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise GeneratorError(f"Generator timed out with seed={seed}.") from exc

    if proc.returncode != 0:
        raise GeneratorError(
            f"Generator failed (seed={seed}), exit code {proc.returncode}.\n"
            f"stderr:\n{proc.stderr.strip()[:2000]}"
        )
    if not proc.stdout.strip():
        raise GeneratorError(f"Generator failed to generate input (seed={seed}).")
    return proc.stdout


def build_test_cases(
    generator_code: str,
    solution_runnable: Runnable,
    workdir: Path,
    count: int | None = None,
) -> list[TestCase]:
    count = count or settings.default_test_count
    workdir.mkdir(parents=True, exist_ok=True)

    generator_path = workdir / "generator.py"
    generator_path.write_text(generator_code, encoding="utf-8")

    cases: list[TestCase] = []
    for seed in range(count):
        input_text = _run_generator(generator_path, seed)
        try:
            output_text = run_with_input(solution_runnable, input_text)
        except RuntimeExecError as exc:
            raise exc
        cases.append(TestCase(index=seed, input_text=input_text, output_text=output_text))
    return cases


def write_test_files(cases: list[TestCase], tests_dir: Path) -> None:
    tests_dir.mkdir(parents=True, exist_ok=True)
    for case in cases:
        (tests_dir / f"{case.index:03d}.in").write_text(case.input_text, encoding="utf-8")
        (tests_dir / f"{case.index:03d}.out").write_text(case.output_text, encoding="utf-8")
