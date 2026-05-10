from nano_eval.evaluators.base import BaseEvaluator
from nano_eval.evaluators.contains import ContainsEvaluator
from nano_eval.evaluators.regex import RegexEvaluator
from nano_eval.evaluators.exact import ExactMatchEvaluator
from nano_eval.config.schema import EvaluatorConfig, JudgeConfig


def get_evaluator(cfg: EvaluatorConfig, judge_cfg: JudgeConfig | None = None) -> BaseEvaluator:
    if cfg.type == "contains":
        return ContainsEvaluator(cfg)
    if cfg.type == "regex":
        return RegexEvaluator(cfg)
    if cfg.type == "exact":
        return ExactMatchEvaluator(cfg)
    if cfg.type == "llm-judge":
        from nano_eval.evaluators.llm_judge import LLMJudgeEvaluator
        return LLMJudgeEvaluator(
            cfg=judge_cfg or JudgeConfig(),
            criteria=cfg.criteria,
            min_score=cfg.min_score,
        )
    raise ValueError(f"Unknown evaluator type: {cfg.type}")
