from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig

try:
    import openai as _openai_module
    _available = True
except ImportError:
    _available = False


class GroqRunner(BaseModelRunner):
    def __init__(self, cfg: ModelConfig):
        if not _available:
            raise ImportError("openai package required for Groq. Install: pip install nano-eval[groq]")
        import os
        self._client = _openai_module.OpenAI(
            api_key=os.environ.get("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1",
        )
        self._cfg = cfg

    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        content = f"{context}\n\n{prompt}" if context else prompt
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
