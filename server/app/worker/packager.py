import zipfile
from pathlib import Path

_SOLUTION_EXT = {"python": "py", "cpp": "cpp"}


def package_problem(
    problem_dir: Path,
    content_md: str,
    solution_code: str,
    language: str,
    tests_dir: Path,
    zip_path: Path,
) -> Path:
    problem_dir.mkdir(parents=True, exist_ok=True)

    statement_path = problem_dir / "statement.md"
    statement_path.write_text(content_md, encoding="utf-8")

    ext = _SOLUTION_EXT.get(language, "txt")
    solution_path = problem_dir / f"solution.{ext}"
    solution_path.write_text(solution_code, encoding="utf-8")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(statement_path, arcname="statement.md")
        zf.write(solution_path, arcname=solution_path.name)
        for test_file in sorted(tests_dir.glob("*")):
            zf.write(test_file, arcname=f"tests/{test_file.name}")

    return zip_path
