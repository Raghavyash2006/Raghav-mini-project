from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Content Localization"
    debug: bool = True
    database_url: str = Field("sqlite:///./localization.db", validation_alias="DATABASE_URL")
    openai_api_key: str = Field(default="your_openai_api_key_here", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", validation_alias="OPENAI_MODEL")
    google_api_key: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-pro", validation_alias="GEMINI_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True
        extra = "ignore"


settings = Settings()
