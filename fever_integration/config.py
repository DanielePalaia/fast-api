from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PROVIDER_URL: str = "https://provider.code-challenge.feverup.com/api/events"
    DB_URL: str = "postgresql+psycopg2://fever_user:fever_pass@localhost:5432/fever_db"
    REFRESH_TIMEOUT: int = 300

    class Config:
        env_file = ".env"


settings = Settings()
