from app.agents.base import run_agent


def content_agent(question: str, requirement: str, algorithm: str, style: str = "LeetCode") -> str:
    return run_agent(
        role="Content/Vibe Agent",
        instruction=(
            f"Biên soạn đề bài lập trình hoàn chỉnh bằng Markdown theo đúng văn phong "
            f"'{style}'. Bài viết PHẢI có các mục: Mô tả bài toán, Input format, Output "
            f"format theo Phong cách Input/Output của các đề ICPC, IOI (tức là cần ghi rõ từng dòng chứa những giá trị gì), "
            "Constraints, ít nhất 1 Ví dụ (Input/Output kèm giải thích ngắn nếu "
            f"cần). KHÔNG lộ trường hợp biên/lời giải/thuật toán/giả định chi tiết trong đề bài."
        ),
        context=(
            f"Yêu cầu gốc:\n{question}\n\nRequirement:\n{requirement}\n\n"
            f"Algorithm (chỉ dùng để đảm bảo đề bài consistent, không in ra):\n{algorithm}"
        ),
    )
