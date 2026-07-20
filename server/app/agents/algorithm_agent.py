from app.agents.base import run_agent


def algorithm_agent(question: str, requirement: str, feedback: str | None = None) -> str:
    context = f"Yêu cầu gốc:\n{question}\n\nRequirement đã duyệt:\n{requirement}"
    if feedback:
        context += f"\n\nPhản biện của người dùng cần xử lý:\n{feedback}"
    return run_agent(
        role="Algorithm Agent",
        instruction=(
            "Đề xuất hướng giải thuật tối ưu (hoặc hiện thực hóa hướng giải người dùng "
            "cung cấp nếu có). Nêu chứng minh/ý tưởng ngắn gọn, độ phức tạp thời gian và "
            "bộ nhớ (Big-O), cùng các bẫy triển khai (implementation pitfalls) cần lưu ý. "
            "KHÔNG viết đề bài hoàn chỉnh, KHÔNG viết code đầy đủ."
        ),
        context=context,
    )
