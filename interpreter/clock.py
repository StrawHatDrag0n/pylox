from __future__ import annotations
import time
import typing
from typing import Any, List
from interpreter.lox_callable import LoxCallable
if typing.TYPE_CHECKING:
    from interpreter.interpreter import Interpreter

class Clock(LoxCallable):
    def arity(self) -> int:
        return 0
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        return time.time()
    
    def __str__(self) -> str:
        return "<native fn>"

    def __repr__(self) -> str:
        return self.__str__()
