from nano_eval.evaluators.base import BaseEvaluator, EvalResult
from nano_eval.config.schema import EvaluatorConfig


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, cfg: EvaluatorConfig):
        self._value = cfg.value
        self._case_sensitive = cfg.case_sensitive

    def evaluate(self, output: str, case) -> EvalResult:
        a = output.strip()
        b = self._value.strip()
        if not self._case_sensitive:
            a = a.lower()
            b = b.lower()
        passed = a == b
        score = 1.0 if passed else 0.0
        reason = "exact match" if passed else "output did not match expected string"
        return EvalResult(passed=passed, score=score, reason=reason)
