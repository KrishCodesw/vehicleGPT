from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VGPT_", env_file=".env", extra="ignore")

    profile: str = Field(default="dev")
    data_dir: str = Field(default="data")
    can_interface: str = Field(default="virtual")
    llm_url: str = Field(default="http://127.0.0.1:8080")
    sim_seed: int = Field(default=42)
    clock: str = Field(default="wall")
    tokens: str = Field(default="driver:dev,service:dev")