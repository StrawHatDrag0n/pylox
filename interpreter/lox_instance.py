import typing

from interpreter.lox_function import LoxFunction
from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token
if typing.TYPE_CHECKING:
    from interpreter.lox_class import LoxClass



class LoxInstance:
    def __init__(self, klass: 'LoxClass') -> None:
        self.klass: LoxClass = klass
        self.fields: dict[str, typing.Any] = dict()

    def __repr__(self) -> str:
        return self.klass.name + " instance"
    
    def get(self, name: Token) -> typing.Any:
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        
        method: typing.Optional[LoxFunction] = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)
        
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: typing.Any):
        self.fields[name.lexeme] = value