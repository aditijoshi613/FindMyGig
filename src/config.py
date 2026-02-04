"""Configurable settings for the live music agent (YAML + env for secrets)."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class AgentConfig:
    """LLM and agent settings. Loaded from YAML; API key from env."""

    model: str
    temperature: float
    api_key: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> "AgentConfig":
        """Load agent config from config.yaml. Env overrides: OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_API_KEY."""
        if path is None:
            path = Path(__file__).resolve().parent.parent / "config.yaml"
        raw: dict[str, Any] = {}
        if path.exists():
            with open(path) as f:
                raw = yaml.safe_load(f) or {}
        agent = raw.get("agent") or {}
        return cls(
            model=os.environ.get("OPENAI_MODEL") or agent.get("model", "gpt-4o"),
            temperature=float(
                os.environ.get("OPENAI_TEMPERATURE")
                or agent.get("temperature", 0)
            ),
            api_key=os.environ.get("OPENAI_API_KEY") or None,
        )

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Backward compat: load from YAML (env still overrides)."""
        return cls.from_yaml()
