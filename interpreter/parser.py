from typing import List, Optional
import typing

from interpreter.expr import Expr, BinaryExpr, SetExpr, ThisExpr, UnaryExpr, LiteralExpr, GroupingExpr, TernaryExpr, VarExpr, AssignExpr, LogicalExpr, CallExpr, GetExpr, SuperExpr
from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.parse_error import ParseError
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType
from interpreter.stmt import BlockStmt, Stmt, PrintStmt, ExpressionStmt, VarStmt, IfStmt, WhileStmt, BreakStmt, FunctionStmt, ReturnStmt, ClassStmt


class Parser:
    def __init__(self, error_handler: LoxErrorHandler, tokens: List[Token]):
        self.error_handler = error_handler
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = list()
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        return statements

    def expression(self):
        return self.assignment()

    def assignment(self) -> Expr:
        expr: Expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if isinstance(expr, VarExpr):
                name: Token = typing.cast(VarExpr, expr).name
                return AssignExpr(name , value)
            elif isinstance(expr, GetExpr):
                expr = typing.cast(GetExpr, expr)
                return SetExpr(expr.obj, expr.name, value)
            self.error(equals, 'Invalid assignment target.')
        return expr

    def logical_or(self):
        expr: Expr = self.logical_and()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.logical_and()
            expr = LogicalExpr(expr, operator, right)
        
        return expr

    def logical_and(self):
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = LogicalExpr(expr, operator, right)
        
        return expr

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function_declaration("function")
            if self.match(TokenType.VAR):
                return self.variable_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None
        
    def class_declaration(self):
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        
        superclass: Optional[VarExpr] = None

        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = VarExpr(self.previous())
        
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: List[FunctionStmt] = list()
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function_declaration("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStmt(name, superclass, methods)

    def function_declaration(self, kind: str):
        name: Optional[Token] = Token(TokenType.IDENTIFIER, 'anon_func', None, -1)
        if self.check(TokenType.IDENTIFIER):
            name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: List[Token] = list()

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.") 

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: List[Stmt] = self.block()
        return FunctionStmt(name, parameters, body)


    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        return self.expression_statement()

    def break_statement(self):
        keyword: Token = self.previous() 
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break';")
        return BreakStmt(keyword)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer: Optional[Stmt] = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        increment: Optional[Expr] = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self.statement()

        if increment:
            body = BlockStmt([body, ExpressionStmt(increment)])

        if condition is None:
            condition = LiteralExpr(True)
        
        body = WhileStmt(condition, body)

        if initializer:
            body = BlockStmt([initializer, body])

        return body 


    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while' condition.")
        body: Stmt = self.statement()
        return WhileStmt(condition, body)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' asfter 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        thenBranch: Stmt = self.statement()
        elseBranch: Optional[Stmt] = None

        if self.match(TokenType.ELSE):
            elseBranch = self.statement()
            
        return IfStmt(condition, thenBranch, elseBranch)


    def print_statement(self):
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    def return_statement(self):
        keyword: Token = self.previous()
        value: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(keyword, value) 

    def variable_declaration(self):
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Optional[Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)

    def expression_statement(self):
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExpressionStmt(expr)

    def block(self) -> List[Stmt]:
        statements: List[Stmt] = list()

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.RIGHT_BRACE, 'Expect \'}\' after block.')
        return statements

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
            right: Expr = typing.cast(Expr, self.unary())
            return UnaryExpr(operator, right)
        return self.call()
    
    def call(self):
        expr: Optional[Expr] = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = typing.cast(Expr, expr)
                expr = GetExpr(expr, name)
            else:
                break
        return expr

    def finishCall(self, callee: Optional[Expr]):
        arguments: List[Expr] = list()
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return CallExpr(callee, paren, arguments)

    def primary(self):
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        if self.match(TokenType.SUPER):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method: Token = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return SuperExpr(keyword, method)
        if self.match(TokenType.THIS):
            return ThisExpr(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return VarExpr(self.previous())
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
        if self.peek().token_type == TokenType.FUN:
            return self.declaration()
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