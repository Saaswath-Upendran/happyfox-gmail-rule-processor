from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    google_credentials_path: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    google_token_path: str = os.getenv("GOOGLE_TOKEN_PATH", "token.json")


    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "gmail_rules")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")


    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "./logs")


    def database_url(self) -> str:
        return (
        f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
        f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
