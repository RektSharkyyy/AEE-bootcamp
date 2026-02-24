"""
Model routing utilities.

Automatically selects appropriate model tier based on prompt technique:
- Reasoning techniques (cot, tot) → reasoning models
- General techniques → general models
"""

import yaml
from pathlib import Path
from typing import Literal, Optional


def pick_model(
    provider: Literal["openai", "google", "groq"],
    technique: str,
    tier: Optional[Literal["general", "strong", "reason"]] = None,
    config_path: str = "config/models.yaml",
) -> str:
    """
    Select appropriate model based on provider and technique.
    """
    config_file = Path(config_path)

    # If config file doesn't exist, try relative to this file's location
    if not config_file.exists():
        # Try relative to utils directory (project root)
        utils_dir = Path(__file__).parent
        project_root = utils_dir.parent
        config_file = project_root / "config" / "models.yaml"

    if not config_file.exists():
        raise FileNotFoundError(
            f"Model config not found. Tried:\n"
            f"  - {config_path}\n"
            f"  - {config_file}\n"
            f"Current working directory: {Path.cwd()}"
        )

# පරණ එක:
    # with open(config_file, "r") as f:

    # අලුත් එක:
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if provider not in config:
        raise KeyError(f"Provider '{provider}' not found in {config_path}")

    # Determine tier based on technique if not explicitly provided
    if tier is None:
        technique_lower = technique.lower()

        # Reasoning techniques require reasoning models
        if any(x in technique_lower for x in ["cot", "tot", "reason", "think"]):
            tier = "reason"
        # Strong/complex techniques benefit from stronger models
        elif any(x in technique_lower for x in ["strong", "complex", "advanced"]):
            tier = "strong"
        # Default to general tier
        else:
            tier = "general"

    if tier not in config[provider]:
        # Fallback to general if requested tier not available
        tier = "general"

    return config[provider][tier]


def list_available_models(config_path: str = "config/models.yaml") -> dict[str, dict]:
    """List all available models from config."""
    config_file = Path(config_path)

    if not config_file.exists():
        utils_dir = Path(__file__).parent
        project_root = utils_dir.parent
        config_file = project_root / "config" / "models.yaml"

    if not config_file.exists():
        return {}

# පරණ එක:
    # with open(config_file, "r") as f:

    # අලුත් එක:
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_context_window(model: str) -> int:
    """Get approximate context window size for a model."""
    model_lower = model.lower()

    # OpenAI models
    if any(x in model_lower for x in ["gpt-4o", "o3", "o1", "gpt-4"]):
        return 128_000
    if "gpt-3.5" in model_lower:
        return 16_385

    # Google Gemini models (Updated for 2026/latest models)
    if "gemini-3" in model_lower:
        return 2_000_000  # Assuming expanded context for newer models
    if "gemini-2" in model_lower:
        return 2_000_000
    if "gemini-1.5" in model_lower:
        return 1_000_000

    # Groq / Open Source models
    if "llama-3.1" in model_lower or "llama-3.2" in model_lower:
        return 131_072
    if "deepseek-r1" in model_lower:
        return 65_536

    # Default conservative estimate
    return 8_000


def should_use_reasoning_model(technique: str) -> bool:
    """Check if technique requires reasoning model."""
    from .config_loader import get_config, should_auto_route_reasoning, get_reasoning_techniques

    if not should_auto_route_reasoning():
        return False

    technique_lower = technique.lower()
    reasoning_techniques = get_reasoning_techniques()

    # Check exact matches first
    if technique_lower in reasoning_techniques:
        return True

    # Check substring matches
    return any(keyword in technique_lower for keyword in reasoning_techniques)
