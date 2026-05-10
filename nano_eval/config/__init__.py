from nano_eval.config.schema import EvalConfig, ModelConfig, JudgeConfig, EvaluatorConfig, CaseConfig
import yaml
from pathlib import Path


def load_config(path: str | Path) -> EvalConfig:
    text = Path(path).read_text(encoding="utf-8")
    raw = yaml.safe_load(text)
    return EvalConfig.model_validate(raw)
