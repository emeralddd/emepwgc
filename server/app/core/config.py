import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # OpenRouter
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )

    # Workers
    sessions_dir: str = os.getenv("SESSIONS_DIR", "sessions")
    default_test_count: int = int(os.getenv("DEFAULT_TEST_COUNT", "20"))
    exec_timeout_seconds: int = int(os.getenv("EXEC_TIMEOUT_SECONDS", "5"))
    max_solution_fix_attempts: int = int(os.getenv("MAX_SOLUTION_FIX_ATTEMPTS", "2"))

    def validate(self) -> None:
        if not self.openrouter_api_key:
            raise ValueError(
                "Missing OPENROUTER_API_KEY environment variable. Please set it in your .env file."
            )

settings = Settings()
