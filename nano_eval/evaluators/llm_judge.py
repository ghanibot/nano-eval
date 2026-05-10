import re
import anthropic
from nano_eval.evaluators.base import BaseEvaluator, EvalResult
from nano_eval.config.schema import JudgeConfig


class LLMJudgeEvaluator(BaseEvaluator):
    def __init__(self, cfg: JudgeConfig, criteria: str = "", min_score: int = 4):
        self._cfg = cfg
        self._criteria = criteria or "accuracy, clarity, completeness"
        self._min_score = min_score
        self._client = anthropic.Anthropic()

    def evaluate(self, output: str, case) -> EvalResult:
        system = (
            "You are an evaluator. Score this AI output 1-5. "
            "Reply with ONLY: SCORE: <n>\nREASON: <one sentence>"
        )
        user = (
            f"Input: {case.input}\n"
            f"Output: {output}\n"
            f"Criteria: {self._criteria}"
        )
        resp = self._client.messages.create(
            model=self._cfg.model,
            max_tokens=128,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = resp.content[0].text.strip()

        score_match = re.search(r"SCORE:\s*([1-5])", text)
        reason_match = re.search(r"REASON:\s*(.+)", text, re.DOTALL)

        raw_score = int(score_match.group(1)) if score_match else 1
        reason = reason_match.group(1).strip() if reason_match else text

        passed = raw_score >= self._min_score
        score_normalized = raw_score / 5.0
        full_reason = f"score {raw_score}/5 — {reason}"
        return EvalResult(passed=passed, score=score_normalized, reason=full_reason)
