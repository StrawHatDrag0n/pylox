from typing import Any, Optional, Self
import typing
from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token


class Environment:
    def __init__(self, enclosing: Optional[Self] = None) -> None:
        self.enclosing: Optional[Self] = enclosing
        self.names: dict[str, int] = dict()
        self.values = list()

    def define(self, name: str, value: Any) -> None:
        self.values.append(value)
        self.names[name] = len(self.values)

    def ancestor(self, distance: int) -> Self:
        environment: Self = self
        for i in range(distance):
            environment = typing.cast(Self, environment.enclosing)
        return environment

    def get_at(self, distance: int, name: str, idx: int):
        return self.ancestor(distance).values[idx]

    def assign_at(self, distance: int, name: Token, value: Any, idx: int):
        environment =  self.ancestor(distance)
        environment.names[name.lexeme] = idx
        environment.values[idx] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.names:
            idx: int = self.names[name.lexeme]
            return self.values[idx]
        if self.enclosing:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.names:
            idx: int = self.names[name.lexeme]
            self.values[idx] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")