from abc import ABC, abstractmethod


class BaseModelRunner(ABC):
    @abstractmethod
    def run(self, prompt: str, system: str = "", context: str = "") -> tuple[str, int]:
        ...
