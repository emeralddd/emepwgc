from app.agents.base import run_agent

_LANG_TAG = {"python": "python", "cpp": "cpp"}


def solution_code_agent(
    content: str,
    algorithm: str,
    language: str = "python",
    fix_feedback: str | None = None,
) -> str:
    tag = _LANG_TAG.get(language, "python")
    context = (
        f"Đề bài:\n{content}\n\nHướng giải đã duyệt:\n{algorithm}\n\n"
        f"Ngôn ngữ bắt buộc: {language}."
    )
    if fix_feedback:
        context += (
            f"\n\nLần trước code bị lỗi khi chạy thử, cần sửa lại. "
            f"Chi tiết lỗi:\n{fix_feedback}"
        )
    return run_agent(
        role="Solution Code Agent",
        instruction=(
            f"Viết đáp án chuẩn (reference solution) bằng {language}, chỉ dùng thư viện "
            f"chuẩn (standard library), đọc từ stdin và in kết quả ra stdout đúng theo "
            f"Output format của đề bài. "
            f"BẮT BUỘC: toàn bộ code đặt trong ĐÚNG MỘT code block dạng "
            f"```{tag}\\n<code>\\n```. Có thể thêm giải thích ngắn gọn TRƯỚC hoặc SAU "
            f"code block, nhưng không được có code block thứ hai."
        ),
        context=context,
    )
