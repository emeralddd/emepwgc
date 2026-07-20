from app.core.llm import get_llm


def run_agent(role: str, instruction: str, context: str, temperature: float = 0.2) -> str:
    llm = get_llm(temperature=temperature)
    response = llm.invoke(
        [
            {"role": "system", "content": f"Bạn là {role}. {instruction}"},
            {"role": "user", "content": context},
        ]
    )
    return response.content
