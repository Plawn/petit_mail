from abc import ABC, abstractmethod
from typing import Callable, Dict


class RenderFunctions(ABC):
    @abstractmethod
    def get_functions() -> Dict[str, Callable[..., str]]:
        ...
