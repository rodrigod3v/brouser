"""Config central — unica porta de entrada de variaveis de ambiente."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelRouting(StrEnum):
    AUTO = "auto"
    FREE = "free"
    PAID = "paid"


class Settings(BaseSettings):
    """Tudo que o brouser precisa, lido de .env (ver .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM principal
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Tier gratuito
    llm_free_base_url: str = ""
    llm_free_api_key: str = ""
    llm_free_model: str = ""
    model_routing: ModelRouting = ModelRouting.AUTO

    # Jev / TypeSafe
    typesafe_api_key: str = ""
    jev_base_url: str = "https://api.typesafe.ai"
    jev_model: str = "jev-latest"
    jev_gate_enabled: bool = True
    jev_verify_done: bool = False

    # Browser
    brouser_headless: bool = False
    brouser_channel: str = "chromium"
    brouser_nav_timeout_ms: int = 30_000
    brouser_max_elements: int = 80

    # Agente
    brouser_max_steps: int = 25
    brouser_profile_dir: str = ".brouser/profile"

    # Obsidian
    brouser_obsidian_vault: str = ""
    brouser_memory_disabled: bool = False

    # Skills
    brouser_skills_enabled: bool = True

    @property
    def vault_path(self) -> Path | None:
        return Path(self.brouser_obsidian_vault) if self.brouser_obsidian_vault else None

    @property
    def free_tier_configured(self) -> bool:
        return bool(self.llm_free_base_url and self.llm_free_api_key and self.llm_free_model)


def get_settings() -> Settings:
    return Settings()
