import json
import urllib.request
from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig


class OllamaRunner(BaseModelRunner):
    """Calls local Ollama server at http://localhost:11434 (no extra deps)."""

    def __init__(self, cfg: ModelConfig):
        import os
        self._base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self._cfg = cfg

    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        content = f"{context}\n\n{prompt}" if context else prompt
        messages = []
        sys = system or self._cfg.system
        if sys:
            messages.append({"role": "system", "content": sys})
        messages.append({"role": "user", "content": content})

        payload = json.dumps({
            "model": self._cfg.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": self._cfg.max_tokens,
                "temperature": self._cfg.temperature,
            },
        }).encode()

        req = urllib.request.Request(
            f"{self._base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            raise RuntimeError(
                f"Ollama request failed. Is Ollama running? ({e})"
            ) from e

        text = data.get("message", {}).get("content", "")
        usage = data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
        return text, usage
