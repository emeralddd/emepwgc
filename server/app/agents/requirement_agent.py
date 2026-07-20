from app.agents.base import run_agent


def requirement_agent(question: str) -> str:
    return run_agent(
        role="Requirement Agent",
        instruction=(
            "Làm rõ ý tưởng bài toán thô của người dùng. Xác định rõ: input/output, "
            "giới hạn (constraints) cụ thể (số liệu), các trường hợp biên (edge cases), "
            "và các giả định còn mơ hồ. Trình bày bằng Markdown, có tiêu đề rõ ràng. "
            "KHÔNG thiết kế thuật toán, KHÔNG viết code."
        ),
        context=question,
    )
