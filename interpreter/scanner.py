from typing import List

from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType


class Scanner:
    KEYWORDS = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, error_handler: LoxErrorHandler, source_code: str) -> None:
        self.error_handler = error_handler
        self.source_code: str = source_code
        self.tokens: List[Token] = list()
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        match c:
            case '?':
                self.add_token(TokenType.QUESTION_MARK)
            case ':':
                self.add_token(TokenType.COLON)
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '*':
                self.add_token(TokenType.STAR)
            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    # A comment goes until the end of the line.
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match('*'):
                    # Multiline comment
                    count = 1
                    while count and not self.is_at_end():
                        if self.peek() == '/' and self.peek_next() == '*':
                            self.advance()
                            count += 1
                        elif self.peek() == '*' and self.peek_next() == '/':
                            self.advance()
                            count -= 1
                        elif self.peek() == '\n':
                            self.line += 1
                        self.advance()
                    if count:
                        self.error_handler.error_on_line(self.line, 'Multiline comment not closed.')
                else:
                    self.add_token(TokenType.SLASH)
            case ' ':
                # Ignore Whitespace
                pass
            case '\r':
                # Ignore Return Carriage
                pass
            case '\t':
                # Ignore Tabs
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    self.error_handler.error_on_line(self.line, "Unexpected character.")

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text = self.source_code[self.start:self.current]
        token_type = self.KEYWORDS.get(text)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source_code[self.start:self.current]))

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.error_handler.error_on_line(self.line, "Unterminated String")
            return
        self.advance()
        value = self.source_code[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def match(self, expected_char: str) -> bool:
        """
        It only consumes the character if it matches the expected_char
        :param expected_char:
        :return:
        """
        if self.is_at_end(): return False
        if self.source_code[self.current] != expected_char: return False
        self.current += 1
        return True

    def peek(self) -> str:
        """
        Looks ahead the current position
        :return:
        """
        if self.is_at_end(): return '\0';
        return self.source_code[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source_code): return '\0'
        return self.source_code[self.current + 1]

    @staticmethod
    def is_alpha(c: str) -> bool:
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c == '_')

    def is_alphanumeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    @staticmethod
    def is_digit(c) -> bool:
        return '0' <= c <= '9'

    def is_at_end(self) -> bool:
        """
        Checks if we are the end of the source_code.
        :return:
        """
        return self.current >= len(self.source_code)

    def add_token(self, token_type: TokenType, literal: object = None):
        """
        Adds token to the tokens list
        :param token_type:
        :param literal:
        :return:
        """
        token_text = self.source_code[self.start: self.current]
        self.tokens.append(Token(token_type, token_text, literal, self.line))

    def advance(self):
        """
        Consumes a character at current position in source_code
        :return:
        """
        c = self.source_code[self.current]
        self.current += 1
        return c
