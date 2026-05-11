from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig


def get_runner(cfg: ModelConfig) -> BaseModelRunner:
    if cfg.provider == "anthropic":
        from nano_eval.runners.anthropic import AnthropicRunner
        return AnthropicRunner(cfg)
    if cfg.provider == "openai":
        from nano_eval.runners.openai import OpenAIRunner
        return OpenAIRunner(cfg)
    if cfg.provider == "groq":
        from nano_eval.runners.groq import GroqRunner
        return GroqRunner(cfg)
    if cfg.provider == "gemini":
        from nano_eval.runners.gemini import GeminiRunner
        return GeminiRunner(cfg)
    if cfg.provider == "ollama":
        from nano_eval.runners.ollama import OllamaRunner
        return OllamaRunner(cfg)
    if cfg.provider == "mistral":
        from nano_eval.runners.mistral import MistralRunner
        return MistralRunner(cfg)
    raise ValueError(f"Unknown provider: {cfg.provider!r}. Supported: anthropic, openai, groq, gemini, ollama, mistral")
