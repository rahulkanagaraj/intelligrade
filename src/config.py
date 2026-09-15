"""Runtime configuration for IntelliGrade Classifier."""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if it exists
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class AppConfig:
    """Application configuration container."""
    ollama_server_url: str = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434/api/generate")
    model_name: str = os.getenv("MODEL_NAME", "llama3:8b")
    mock_mode: bool = os.getenv("MOCK_MODE", "true").lower() in ("true", "1", "yes")
    auto_mock_fallback: bool = os.getenv("AUTO_MOCK_FALLBACK", "true").lower() in ("true", "1", "yes")
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    backoff_factor: float = float(os.getenv("BACKOFF_FACTOR", "1.5"))

    def get_base_url(self) -> str:
        """Derive base server URL (e.g. http://192.168.1.50:11434)."""
        url = self.ollama_server_url.strip()
        if "/api/" in url:
            return url.split("/api/")[0]
        return url.rstrip("/")


# Singleton global config instance
config = AppConfig()


def get_config() -> AppConfig:
    """Retrieve current runtime configuration."""
    return config


def update_config(
    ollama_server_url: str | None = None,
    model_name: str | None = None,
    mock_mode: bool | None = None,
    auto_mock_fallback: bool | None = None,
    request_timeout: int | None = None,
    max_retries: int | None = None,
) -> AppConfig:
    """Update runtime configuration dynamically."""
    global config
    if ollama_server_url is not None:
        config.ollama_server_url = ollama_server_url.strip()
    if model_name is not None:
        config.model_name = model_name.strip()
    if mock_mode is not None:
        config.mock_mode = mock_mode
    if auto_mock_fallback is not None:
        config.auto_mock_fallback = auto_mock_fallback
    if request_timeout is not None:
        config.request_timeout = request_timeout
    if max_retries is not None:
        config.max_retries = max_retries
    return config
