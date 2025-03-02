from __future__ import annotations
import typing
from typing import Any, List
from interpreter.environment import Environment
from interpreter.lox_callable import LoxCallable
from interpreter.return_exception import Return
from interpreter.stmt import FunctionStmt
if typing.TYPE_CHECKING:
    from interpreter.interpreter import Interpreter
    from interpreter.lox_instance import LoxInstance


class LoxFunction(LoxCallable):
    def __init__(self, declaration: FunctionStmt, closure: Environment, is_initializer: bool) -> None:
        self.declaration: FunctionStmt = declaration
        self.closure = closure
        self.is_initializer: bool = is_initializer 

    def bind(self, instance: LoxInstance):
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        environment: Environment = Environment(self.closure)
        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def __repr__(self) -> str:
        return self.__str__()