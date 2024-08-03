from typing import List

from interpreter.expr import Expr, BinaryExpr, UnaryExpr, LiteralExpr, GroupingExpr, TernaryExpr, VariableExpr
from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.parse_error import ParseError
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType
from interpreter.stmt import Stmt, PrintStmt, ExpressionStmt, VarStmt


class Parser:
    def __init__(self, error_handler: LoxErrorHandler, tokens: List[Token]):
        self.error_handler = error_handler
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements: List[Stmt] = list()
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self):
        return self.comma()

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.variable_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    def variable_declaration(self):
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr | None = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)

    def expression_statement(self):
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExpressionStmt(expr)

    def comma(self):
        return self.parse_binary_expr(self.ternary, [TokenType.COMMA])

    def ternary(self):
        expr: Expr = self.equality()
        if self.match(TokenType.QUESTION_MARK):
            then_branch = self.comma()
            self.consume(TokenType.COLON, "Ternary expression needs a colon.")
            else_branch: Expr = self.equality()
            expr = TernaryExpr(expr, then_branch, else_branch)
        return expr

    def equality(self):
        return self.parse_binary_expr(self.comparison, [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL])

    def comparison(self):
        return self.parse_binary_expr(self.term, [TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS,
                                                  TokenType.LESS_EQUAL])

    def term(self):
        return self.parse_binary_expr(self.factor, [TokenType.MINUS, TokenType.PLUS])

    def factor(self):
        return self.parse_binary_expr(self.unary, [TokenType.SLASH, TokenType.STAR])

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return UnaryExpr(operator, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        if self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.equality()
            return None
        if self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.comparison()
            return None
        if self.match(TokenType.PLUS):
            self.error(self.previous(), "Missing left-hand operand.")
            self.term()
            return None
        if self.match(TokenType.SLASH, TokenType.STAR):
            self.error(self.previous(), "Missing left-hand operand.")
            self.factor()
            return None


        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *token_types) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, token_type) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def parse_binary_expr(self, higher_precedence, token_types) -> Expr:
        expr: Expr = higher_precedence()
        while self.match(*token_types):
            operator: Token = self.previous()
            right: Expr = higher_precedence()
            expr = BinaryExpr(expr, operator, right)
        return expr


    def error(self, token: Token, message: str):
        self.error_handler.error_on_token(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            match self.peek().token_type:
                case TokenType.CLASS:
                    return
                case TokenType.FUN:
                    return
                case TokenType.VAR:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.RETURN:
                    return
            self.advance()