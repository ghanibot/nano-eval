from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig

try:
    import openai as _openai_module
    _openai_available = True
except ImportError:
    _openai_available = False


class OpenAIRunner(BaseModelRunner):
    def __init__(self, cfg: ModelConfig):
        if not _openai_available:
            raise ImportError(
                "openai package is not installed. Install it with: pip install nano-eval[openai]"
            )
        self._client = _openai_module.OpenAI()
        self._cfg = cfg

    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        if context:
            content = f"{context}\n\n{prompt}"
        else:
            content = prompt

        messages = []
        sys = system or self._cfg.system
        if sys:
            messages.append({"role": "system", "content": sys})
        messages.append({"role": "user", "content": content})

        resp = self._client.chat.completions.create(
            model=self._cfg.model,
            max_tokens=self._cfg.max_tokens,
            temperature=self._cfg.temperature,
            messages=messages,
        )
        text = resp.choices[0].message.content or ""
        usage = resp.usage
        tokens = (usage.prompt_tokens + usage.completion_tokens) if usage else 0
        return text, tokens
