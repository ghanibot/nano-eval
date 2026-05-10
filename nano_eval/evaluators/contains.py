from nano_eval.evaluators.base import BaseEvaluator, EvalResult
from nano_eval.config.schema import EvaluatorConfig


class ContainsEvaluator(BaseEvaluator):
    def __init__(self, cfg: EvaluatorConfig):
        self._value = cfg.value
        self._case_sensitive = cfg.case_sensitive

    def evaluate(self, output: str, case) -> EvalResult:
        haystack = output if self._case_sensitive else output.lower()
        needle = self._value if self._case_sensitive else self._value.lower()
        passed = needle in haystack
        score = 1.0 if passed else 0.0
        reason = f"'{self._value}' {'found' if passed else 'not found'} in output"
        return EvalResult(passed=passed, score=score, reason=reason)
