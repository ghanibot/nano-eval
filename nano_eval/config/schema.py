from pydantic import BaseModel, Field
from typing import Literal, Union


class ModelConfig(BaseModel):
    provider: Literal["anthropic", "openai"] = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 1024
    temperature: float = 0.0
    system: str = ""


class JudgeConfig(BaseModel):
    model: str = "claude-haiku-4-5-20251001"
    provider: Literal["anthropic", "openai"] = "anthropic"


class EvaluatorConfig(BaseModel):
    type: Literal["contains", "regex", "exact", "llm-judge"] = "contains"
    value: str = ""
    case_sensitive: bool = False
    min_score: int = 4
    criteria: str = ""


class CaseConfig(BaseModel):
    id: str = ""
    description: str = ""
    input: str
    context: str = ""
    expected: str = ""
    evaluator: Union[str, EvaluatorConfig] = "contains"
    tags: list[str] = Field(default_factory=list)
    skip: bool = False
    min_score: int = 4
    criteria: str = ""


class EvalConfig(BaseModel):
    name: str = "eval"
    model: ModelConfig = Field(default_factory=ModelConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    cases: list[CaseConfig] = Field(default_factory=list)
    max_concurrency: int = 3
    fail_fast: bool = False
