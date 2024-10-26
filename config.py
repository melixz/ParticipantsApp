from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    MAX_LIKES_PER_DAY: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
