from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType


class LoxErrorHandler:
    def __init__(self):
        self.HAS_ERROR = False
        self.HAS_RUNTIME_ERROR = False;

    def error_on_line(self, line: int, message: str):
        self.report(line, "", message)

    def error_on_token(self, token: Token, message: str):
        if token.token_type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def report(self, line: int, where: str, message: str):
        print(f'[line {line}]: Error {where}: {message}')
        self.HAS_ERROR = True

    def runtime_error(self, error: LoxRuntimeError):
        print(f'{error.message} \n [line {error.token.line}]' )
        self.HAS_RUNTIME_ERROR = True