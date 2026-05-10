import re
from nano_eval.evaluators.base import BaseEvaluator, EvalResult
from nano_eval.config.schema import EvaluatorConfig


class RegexEvaluator(BaseEvaluator):
    def __init__(self, cfg: EvaluatorConfig):
        self._pattern = cfg.value

    def evaluate(self, output: str, case) -> EvalResult:
        match = re.search(self._pattern, output)
        passed = bool(match)
        score = 1.0 if passed else 0.0
        reason = f"pattern '{self._pattern}' {'matched' if passed else 'not matched'} in output"
        return EvalResult(passed=passed, score=score, reason=reason)
