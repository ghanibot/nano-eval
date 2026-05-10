from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig


def get_runner(cfg: ModelConfig) -> BaseModelRunner:
    if cfg.provider == "anthropic":
        from nano_eval.runners.anthropic import AnthropicRunner
        return AnthropicRunner(cfg)
    if cfg.provider == "openai":
        from nano_eval.runners.openai import OpenAIRunner
        return OpenAIRunner(cfg)
    raise ValueError(f"Unknown provider: {cfg.provider}")
