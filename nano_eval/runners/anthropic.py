import anthropic
from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig


class AnthropicRunner(BaseModelRunner):
    def __init__(self, cfg: ModelConfig):
        self._client = anthropic.Anthropic()
        self._cfg = cfg

    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        if context:
            content = f"{context}\n\n{prompt}"
        else:
            content = prompt

        messages = [{"role": "user", "content": content}]

        kwargs: dict = dict(
            model=self._cfg.model,
            max_tokens=self._cfg.max_tokens,
            messages=messages,
        )
        sys = system or self._cfg.system
        if sys:
            kwargs["system"] = sys

        resp = self._client.messages.create(**kwargs)
        text = resp.content[0].text
        tokens = resp.usage.input_tokens + resp.usage.output_tokens
        return text, tokens
