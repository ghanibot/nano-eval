from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EvalResult:
    passed: bool
    score: float
    reason: str = ""


class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, output: str, case) -> EvalResult:
        ...
