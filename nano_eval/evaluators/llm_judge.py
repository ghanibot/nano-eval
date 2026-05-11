import re
from nano_eval.evaluators.base import BaseEvaluator, EvalResult
from nano_eval.config.schema import JudgeConfig, ModelConfig


class LLMJudgeEvaluator(BaseEvaluator):
    def __init__(self, cfg: JudgeConfig, criteria: str = "", min_score: int = 4):
        self._cfg = cfg
        self._criteria = criteria or "accuracy, clarity, completeness"
        self._min_score = min_score

        from nano_eval.runners.factory import get_runner
        judge_model_cfg = ModelConfig(
            provider=cfg.provider,
            model=cfg.model,
            max_tokens=256,
            temperature=0.0,
            system=(
                "You are an evaluator. Score this AI output 1-5. "
                "Reply with ONLY: SCORE: <n>\nREASON: <one sentence>"
            ),
        )
        self._runner = get_runner(judge_model_cfg)

    def evaluate(self, output: str, case) -> EvalResult:
        user = (
            f"Input: {case.input}\n"
            f"Output: {output}\n"
            f"Criteria: {self._criteria}"
        )
        text, _ = self._runner.run(user)
        text = text.strip()

        score_match = re.search(r"SCORE:\s*([1-5])", text)
        reason_match = re.search(r"REASON:\s*(.+)", text, re.DOTALL)

        raw_score = int(score_match.group(1)) if score_match else 1
        reason = reason_match.group(1).strip() if reason_match else text

        passed = raw_score >= self._min_score
        score_normalized = raw_score / 5.0
        full_reason = f"score {raw_score}/5 — {reason}"
        return EvalResult(passed=passed, score=score_normalized, reason=full_reason)
