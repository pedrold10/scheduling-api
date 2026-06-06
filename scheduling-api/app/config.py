from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://scheduling:scheduling@localhost:5432/scheduling_db"

    model_config = {"env_file": ".env"}


settings = Settings()
