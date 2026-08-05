from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.
    In Cloud Run, GCP_PROJECT_ID and GCP_LOCATION are set via container environment variables.
    """
    gcp_project_id: str = "personal-testing-502307"
    gcp_location: str = "global"
    gemini_model: str = "gemini-3.5-flash"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
