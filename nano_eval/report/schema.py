from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CaseResult:
    case_id: str
    description: str
    input: str
    output: str
    passed: bool
    score: float
    reason: str
    tokens_used: int
    duration_ms: int
    error: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "input": self.input,
            "output": self.output,
            "passed": self.passed,
            "score": self.score,
            "reason": self.reason,
            "tokens_used": self.tokens_used,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "tags": self.tags,
        }


@dataclass
class EvalReport:
    name: str
    model: str
    total: int
    passed: int
    failed: int
    skipped: int
    pass_rate: float
    avg_score: float
    total_tokens: int
    duration_ms: int
    cases: list[CaseResult] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "model": self.model,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "pass_rate": self.pass_rate,
            "avg_score": self.avg_score,
            "total_tokens": self.total_tokens,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at,
            "cases": [c.to_dict() for c in self.cases],
        }
