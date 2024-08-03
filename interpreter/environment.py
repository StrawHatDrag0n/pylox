from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token


class Environment:
    def __init__(self):
        self.map = dict()

    def define(self, name: str, value: any):
        self.map[name] = value

    def get(self, name: Token):
        if name.lexeme in self.map:
            return self.map[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")