from interpreter.lox_token_type import TokenType


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int) -> None:
        self.line = line
        self.literal = literal
        self.lexeme = lexeme
        self.token_type = token_type

    def __str__(self) -> str:
        return f'{self.token_type} {self.lexeme} {self.literal}'

    def __repr__(self) -> str:
        return self.__str__()