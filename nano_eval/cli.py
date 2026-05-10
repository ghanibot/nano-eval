import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from nano_eval.config import load_config
from nano_eval.core.runner import EvalRunner
from nano_eval.report.schema import EvalReport, CaseResult

app = typer.Typer(name="nano-eval", add_completion=False)
console = Console()


@app.command()
def run(
    config: Path = typer.Argument(..., help="Path to eval YAML config"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save report as JSON"),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop on first failure"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Only run cases with this tag"),
):
    cfg = load_config(config)

    if fail_fast:
        cfg = cfg.model_copy(update={"fail_fast": True})

    if tag:
        filtered = [c for c in cfg.cases if tag in c.tags]
        cfg = cfg.model_copy(update={"cases": filtered})

    total_cases = sum(1 for c in cfg.cases if not c.skip)
    console.print(
        f"\nRunning eval: [bold]{cfg.name}[/bold]  "
        f"({total_cases} cases, model: {cfg.model.model})"
    )
    console.print("━" * 44)

    runner = EvalRunner(cfg)
    report = runner.run()

    _print_results(report)

    if output:
        output.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        console.print(f"\nReport saved to [dim]{output}[/dim]")

    if report.failed > 0:
        raise typer.Exit(1)


@app.command()
def show(
    report_path: Path = typer.Argument(..., help="Path to report JSON"),
):
    data = json.loads(report_path.read_text(encoding="utf-8"))
    report = EvalReport(
        name=data["name"],
        model=data["model"],
        total=data["total"],
        passed=data["passed"],
        failed=data["failed"],
        skipped=data["skipped"],
        pass_rate=data["pass_rate"],
        avg_score=data["avg_score"],
        total_tokens=data["total_tokens"],
        duration_ms=data["duration_ms"],
        created_at=data["created_at"],
        cases=[
            CaseResult(
                case_id=c["case_id"],
                description=c["description"],
                input=c["input"],
                output=c["output"],
                passed=c["passed"],
                score=c["score"],
                reason=c["reason"],
                tokens_used=c["tokens_used"],
                duration_ms=c["duration_ms"],
                error=c.get("error", ""),
                tags=c.get("tags", []),
            )
            for c in data["cases"]
        ],
    )
    console.print(f"\nReport: [bold]{report.name}[/bold]  (model: {report.model})")
    console.print(f"Created: [dim]{report.created_at}[/dim]")
    console.print("━" * 44)
    _print_results(report)


def _print_results(report: EvalReport) -> None:
    for case in report.cases:
        icon = "[green]✓[/green]" if case.passed else "[red]✗[/red]"
        evaluator_type = _infer_evaluator_label(case.reason)
        duration = f"{case.duration_ms}ms"
        score_str = f"{case.score:.2f}"
        extra = f"  [dim]{case.reason}[/dim]" if case.reason else ""
        if case.error:
            extra = f"  [red]{case.error}[/red]"
        console.print(
            f"  {icon}  {case.case_id:<20} {evaluator_type:<12} {score_str}   {duration}{extra}"
        )

    console.print()
    pass_pct = f"{report.pass_rate * 100:.0f}%"
    time_s = f"{report.duration_ms / 1000:.1f}s"
    console.print(
        f"Results: [bold]{report.passed}/{report.total}[/bold] passed ({pass_pct})  "
        f"avg score: {report.avg_score:.2f}  "
        f"tokens: {report.total_tokens:,}  "
        f"time: {time_s}"
    )


def _infer_evaluator_label(reason: str) -> str:
    if "score" in reason and "/5" in reason:
        return "llm-judge"
    if "pattern" in reason:
        return "regex"
    if "exact match" in reason or "did not match" in reason:
        return "exact"
    if "found" in reason or "not found" in reason:
        return "contains"
    return "unknown"
