from app.agents.base import run_agent


def test_generator_agent(
    content: str, solution: str, fix_feedback: str | None = None
) -> str:
    context = f"Đề bài:\n{content}\n\nLời giải chuẩn (chỉ để tham khảo format input):\n{solution}"
    if fix_feedback:
        context += f"\n\nScript trước chạy lỗi, cần sửa lại. Chi tiết lỗi:\n{fix_feedback}"
    return run_agent(
        role="Test Generator Agent",
        instruction=(
            "Viết MỘT script Python độc lập (chỉ dùng standard library, ví dụ module "
            "`random`, `sys`) để sinh 1 test input mỗi lần chạy. "
            "BẮT BUỘC: script nhận đúng 1 tham số dòng lệnh `seed` (int) qua sys.argv[1], "
            "dùng `random.seed(seed)`, và chỉ `print()` phần input hợp lệ ra stdout theo "
            "đúng Input format của đề bài (không in log, không in debug). "
            "Với seed = 0, 1, 2... hãy ưu tiên tái tạo các edge case đã nêu trong đề bài "
            "(giá trị nhỏ nhất, lớn nhất, mảng rỗng nếu hợp lệ, v.v.). Seed lớn hơn thì "
            "sinh ngẫu nhiên nhưng vẫn phải thoả constraints. "
            "BẮT BUỘC: toàn bộ code đặt trong ĐÚNG MỘT code block ```python ... ```."
        ),
        context=context,
    )
