from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Browser
    headless: bool = True
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    slow_mo: int = 0

    # Proxy
    proxy_list: list[str] = Field(default_factory=list)
    proxy_strategy: Literal["round_robin", "random", "sticky"] = "round_robin"

    # API export
    api_endpoint: str | None = None
    api_token: str | None = None

    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 60

    # Output
    output_dir: Path = ROOT_DIR / "output"

    # Logging
    log_level: str = "INFO"
    log_format: Literal["console", "json"] = "console"

    # Portals config dir
    portals_config_dir: Path = ROOT_DIR / "config" / "portals"


settings = Settings()
