import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


class CompileError(Exception):
    pass


class RuntimeExecError(Exception):
    pass


@dataclass
class Runnable:
    language: str
    run_cmd: list[str]


def prepare_runnable(language: str, code: str, workdir: Path) -> Runnable:
    workdir.mkdir(parents=True, exist_ok=True)

    if language == "python":
        src = workdir / "solution.py"
        src.write_text(code, encoding="utf-8")
        return Runnable(language="python", run_cmd=["python3", str(src)])

    if language == "cpp":
        src = workdir / "solution.cpp"
        binary = workdir / "solution"
        src.write_text(code, encoding="utf-8")
        proc = subprocess.run(
            ["g++", "-O2", "-std=c++17", "-static-libstdc++", "-static-libgcc", "-static", "-o", str(binary), str(src)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        if proc.returncode != 0:
            raise CompileError(proc.stderr.strip() or "g++ compile failed for an unknown reason.")
        return Runnable(language="cpp", run_cmd=[str(binary)])

    raise ValueError(f"Language not supported: {language}")


def run_with_input(runnable: Runnable, input_text: str) -> str:
    try:
        proc = subprocess.run(
            runnable.run_cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=settings.exec_timeout_seconds,
            check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeExecError(
            f"Execution exceeded allowed time ({settings.exec_timeout_seconds}s) with input:\n{input_text[:300]}"
        ) from exc

    if proc.returncode != 0:
        raise RuntimeExecError(
            f"Program exited with code {proc.returncode}.\nstderr:\n{proc.stderr.strip()[:2000]}\n"
            f"input:\n{input_text[:300]}"
        )
    return proc.stdout
