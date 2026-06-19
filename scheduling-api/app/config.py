from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://scheduling:scheduling@localhost:5432/scheduling_db"

    # Auth
    jwt_secret_key: str = "TROQUE_ESTA_CHAVE_EM_PRODUCAO"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8  # 8 horas

    model_config = {"env_file": ".env"}


settings = Settings()
