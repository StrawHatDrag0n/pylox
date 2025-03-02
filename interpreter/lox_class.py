import typing
from typing import Any, List, Optional

from interpreter.lox_function import LoxFunction
if typing.TYPE_CHECKING:
    from interpreter.interpreter import Interpreter
from interpreter.lox_callable import LoxCallable
from interpreter.lox_instance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: 'LoxClass',methods: dict[str, LoxFunction]) -> None:
        self.name: str = name
        self.superclass: LoxClass = superclass 
        self.methods: dict[str, LoxFunction] = methods

    def __repr__(self) -> str:
        return self.name
    
    def arity(self) -> int:
        initializer: Optional[LoxFunction] = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        instance: LoxInstance = LoxInstance(self)
        initializer: Optional[LoxFunction] = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods.get(name)
        
        if self.superclass:
            return self.superclass.find_method(name)
        
        return None