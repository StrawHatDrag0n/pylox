from typing import Any, Optional, Self
import typing
from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token


class Environment:
    def __init__(self, enclosing: Optional[Self] = None) -> None:
        self.enclosing: Optional[Self] = enclosing
        self.values: dict = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def ancestor(self, distance: int) -> Self:
        environment: Self = self
        for i in range(distance):
            environment = typing.cast(Self, environment.enclosing)
        return environment

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")