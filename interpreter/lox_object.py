from abc import ABC

class LoxObject(ABC):
    def __init__(self, value: Any):
        self._value = value

class LoxString(LoxObject):
    def __init__(self, value: Any):
        super().__init__(value)

class LoxBoolean(LoxObject):
    def __init__(self, value: Any):
        super().__init__(value)

    def __bool__(self):
        return self._value

class LoxFloat(LoxObject):
    def __init__(self, value: Any):
        super().__init__(value)

    def __float__(self):
        pass
