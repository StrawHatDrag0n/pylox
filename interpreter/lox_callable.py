from __future__ import annotations
from abc import ABC, abstractmethod
import typing
from typing import Any, List
if typing.TYPE_CHECKING:
    from interpreter.interpreter import Interpreter

class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        ...
        
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        ...