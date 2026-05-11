from nano_eval.runners.base import BaseModelRunner
from nano_eval.config.schema import ModelConfig

try:
    import google.generativeai as genai
    _available = True
except ImportError:
    _available = False


class GeminiRunner(BaseModelRunner):
    def __init__(self, cfg: ModelConfig):
        if not _available:
            raise ImportError(
                "google-generativeai package required. Install: pip install nano-eval[gemini]"
            )
        import os
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))
        self._cfg = cfg
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )
        system = cfg.system or None
        self._model = genai.GenerativeModel(
            model_name=cfg.model,
            generation_config=generation_config,
            system_instruction=system,
        )

    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        content = f"{context}\n\n{prompt}" if context else prompt

        if system and system != self._cfg.system:
            import google.generativeai as genai
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self._cfg.max_tokens,
                temperature=self._cfg.temperature,
            )
            model = genai.GenerativeModel(
                model_name=self._cfg.model,
                generation_config=generation_config,
                system_instruction=system,
            )
            resp = model.generate_content(content)
        else:
            resp = self._model.generate_content(content)

        text = resp.text or ""
        tokens = 0
        if resp.usage_metadata:
            tokens = (
                (resp.usage_metadata.prompt_token_count or 0)
                + (resp.usage_metadata.candidates_token_count or 0)
            )
        return text, tokens
