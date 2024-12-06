# src/code_reviewer/config/settings.py
from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_key: str = Field("", env="POE_API_KEY")
    max_tokens_per_group: int = Field(12000, env="MAX_TOKENS_PER_GROUP")
    max_retries: int = Field(3, env="MAX_RETRIES")
    delay_between_groups: int = Field(5, env="DELAY_BETWEEN_GROUPS")
    model_name: str = Field("Claude-2-100k", env="MODEL_NAME")

    target_extensions: list = Field(
        default=[".java", ".yml", ".yaml", ".properties", ".xml"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config(config_path: Path) -> Dict[str, Any]:
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def save_config(config: Dict[str, Any], config_path: Path) -> None:
    with open(config_path, "w") as f:
        yaml.dump(config, f)