"""Configurable settings for the live music agent (YAML + env for secrets)."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class AgentConfig:
    """LLM and agent settings. Loaded from YAML; API key from env.

    Supports both OpenAI and Anthropic (Claude). The provider is chosen
    automatically based on which API key is set, or can be forced via the
    ``LLM_PROVIDER`` env var (``openai`` or ``anthropic``).
    """

    provider: str  # "openai" or "anthropic"
    model: str
    temperature: float
    api_key: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> "AgentConfig":
        if path is None:
            path = Path(__file__).resolve().parent.parent / "config.yaml"
        raw: dict[str, Any] = {}
        if path.exists():
            with open(path) as f:
                raw = yaml.safe_load(f) or {}
        agent = raw.get("agent") or {}

        # Determine provider: explicit env var > whichever key is set
        explicit_provider = os.environ.get("LLM_PROVIDER", "").lower()
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

        if explicit_provider == "anthropic" or (not explicit_provider and anthropic_key and not openai_key):
            provider = "anthropic"
            default_model = "claude-sonnet-4-20250514"
            api_key = anthropic_key
        else:
            provider = "openai"
            default_model = "gpt-4o"
            api_key = openai_key

        return cls(
            provider=provider,
            model=os.environ.get("LLM_MODEL") or agent.get("model") or default_model,
            temperature=float(
                os.environ.get("LLM_TEMPERATURE")
                or agent.get("temperature", 0)
            ),
            api_key=api_key,
        )

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Backward compat: load from YAML (env still overrides)."""
        return cls.from_yaml()
