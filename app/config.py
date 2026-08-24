from pydantic_settings import BaseSettings
from pydantic import field_validator


class Config(BaseSettings):
    telegram_bot_token: str
    openai_api_key: str
    database_url: str
    openai_model: str = "gpt-4o"
    openai_search_context_size: str = "high"
    watch_send_hour: int = 9
    watch_send_minute: int = 0
    watch_timezone: str = "Europe/Madrid"
    allowed_telegram_user_ids: str = ""
    max_profiles_per_user: int = 5

    @field_validator("openai_search_context_size")
    @classmethod
    def validate_context_size(cls, v: str) -> str:
        if v not in ("low", "medium", "high"):
            raise ValueError("OPENAI_SEARCH_CONTEXT_SIZE must be low, medium, or high")
        return v

    def allowed_user_ids(self) -> set[int]:
        if not self.allowed_telegram_user_ids.strip():
            return set()
        return {int(uid.strip()) for uid in self.allowed_telegram_user_ids.split(",") if uid.strip()}


config = Config()
