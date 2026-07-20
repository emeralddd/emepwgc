import re

_LANG_ALIASES = {
    "python": ["python", "py"],
    "cpp": ["cpp", "c++", "cxx", "c"],
}


class CodeExtractionError(Exception):
    pass


def extract_code(text: str, language: str) -> str:
    aliases = _LANG_ALIASES.get(language, [language])
    alt = "|".join(re.escape(a) for a in aliases)

    # Match code block with the expected language tag (case-insensitive).
    pattern = rf"```(?:{alt})\s*\n(.*?)```"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    # Get the first code block as a fallback (if any).
    fallback = re.search(r"```[a-zA-Z0-9+]*\s*\n(.*?)```", text, re.DOTALL)
    if fallback:
        return fallback.group(1).strip()

    raise CodeExtractionError(
        f"Cannot extract code block for language {language}."
    )
