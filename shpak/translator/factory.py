from .base import BaseTranslator
from .cli_backend import CLITranslator

def create_translator(cfg: dict, provider_override: str = None, model_override: str = None) -> BaseTranslator:
    """Creates a CLI subscription-based translator (0 API keys required)."""
    active = cfg.get("active_translator", {})
    provider = provider_override or active.get("provider", "agy-cli")
    model = model_override or active.get("model", "auto")

    providers_cfg = cfg.get("providers", {})
    prov_cfg = providers_cfg.get(provider, {})
    prompts = cfg.get("prompts", {})

    if provider in ("claude-cli", "claude"):
        cli_tool = prov_cfg.get("cli_tool", "claude")
    else:
        cli_tool = prov_cfg.get("cli_tool", "agy")

    return CLITranslator(prompts=prompts, cli_tool=cli_tool, model=model)
