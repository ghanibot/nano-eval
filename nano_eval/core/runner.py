import time
import uuid
import concurrent.futures
from nano_eval.config.schema import EvalConfig, CaseConfig, EvaluatorConfig
from nano_eval.evaluators.factory import get_evaluator
from nano_eval.runners.factory import get_runner
from nano_eval.report.schema import CaseResult, EvalReport


class EvalRunner:
    def __init__(self, cfg: EvalConfig):
        self._cfg = cfg
        self._runner = get_runner(cfg.model)

    def run(self) -> EvalReport:
        start = time.monotonic()
        active_cases = []
        skipped = 0

        for i, case in enumerate(self._cfg.cases):
            if case.skip:
                skipped += 1
                continue
            if not case.id:
                case = case.model_copy(update={"id": f"case-{i + 1}"})
            active_cases.append(case)

        results: list[CaseResult] = []
        failed_fast = False

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_concurrency
        ) as executor:
            futures = {executor.submit(self._run_case, c): c for c in active_cases}
            for future in concurrent.futures.as_completed(futures):
                if failed_fast:
                    future.cancel()
                    continue
                result = future.result()
                results.append(result)
                if self._cfg.fail_fast and not result.passed and not result.error == "":
                    failed_fast = True
                elif self._cfg.fail_fast and not result.passed:
                    failed_fast = True

        results.sort(key=lambda r: active_cases.index(
            next(c for c in active_cases if c.id == r.case_id)
        ))

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        scores = [r.score for r in results if not r.error]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        total_tokens = sum(r.tokens_used for r in results)
        duration_ms = int((time.monotonic() - start) * 1000)

        return EvalReport(
            name=self._cfg.name,
            model=self._cfg.model.model,
            total=len(active_cases),
            passed=passed,
            failed=failed,
            skipped=skipped,
            pass_rate=passed / len(active_cases) if active_cases else 0.0,
            avg_score=avg_score,
            total_tokens=total_tokens,
            duration_ms=duration_ms,
            cases=results,
        )

    def _run_case(self, case: CaseConfig) -> CaseResult:
        start = time.monotonic()
        output = ""
        tokens = 0
        error = ""

        try:
            output, tokens = self._runner.run(
                prompt=case.input,
                context=case.context,
            )
        except Exception as exc:
            error = str(exc)
            duration_ms = int((time.monotonic() - start) * 1000)
            return CaseResult(
                case_id=case.id,
                description=case.description,
                input=case.input,
                output="",
                passed=False,
                score=0.0,
                reason="model call failed",
                tokens_used=0,
                duration_ms=duration_ms,
                error=error,
                tags=case.tags,
            )

        eval_cfg = _resolve_evaluator(case)
        evaluator = get_evaluator(eval_cfg, self._cfg.judge)
        result = evaluator.evaluate(output, case)
        duration_ms = int((time.monotonic() - start) * 1000)

        return CaseResult(
            case_id=case.id,
            description=case.description,
            input=case.input,
            output=output,
            passed=result.passed,
            score=result.score,
            reason=result.reason,
            tokens_used=tokens,
            duration_ms=duration_ms,
            error="",
            tags=case.tags,
        )


def _resolve_evaluator(case: CaseConfig) -> EvaluatorConfig:
    if isinstance(case.evaluator, EvaluatorConfig):
        cfg = case.evaluator
        if not cfg.value and case.expected:
            cfg = cfg.model_copy(update={"value": case.expected})
        return cfg

    ev_type = case.evaluator if isinstance(case.evaluator, str) else "contains"

    if ev_type == "llm-judge":
        return EvaluatorConfig(
            type="llm-judge",
            min_score=case.min_score,
            criteria=case.criteria,
        )

    return EvaluatorConfig(
        type=ev_type,
        value=case.expected,
    )
