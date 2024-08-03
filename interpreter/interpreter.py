from typing import List

from interpreter.environment import Environment
from interpreter.expr import ExprVisitor, UnaryExpr, LiteralExpr, GroupingExpr, BinaryExpr, TernaryExpr, Expr, \
    VariableExpr
from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType
from interpreter.stmt import StmtVisitor, PrintStmt, ExpressionStmt, Stmt, VarStmt


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, error_handler: LoxErrorHandler):
        self.error_handler = error_handler
        self.environment = Environment()
    def interpret(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except LoxRuntimeError as error:
            self.error_handler.runtime_error(error)

    def visit_ternary_expr(self, expr: TernaryExpr) -> any:
        pass

    def visit_binary_expr(self, expr: BinaryExpr) -> any:
        left: any = self.evaluate(expr.left)
        right: any = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.GREATER:
                if isinstance(left, str) and isinstance(right, str):
                    return len(str(left)) > len(str(right))
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                if isinstance(left, str) and isinstance(right, str):
                    return len(str(left)) >= len(str(right))
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                if isinstance(left, str) and isinstance(right, str):
                    return len(str(left)) < len(str(right))
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                if isinstance(left, str) and isinstance(right, str):
                    return len(str(left)) <= len(str(right))
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                if (isinstance(left, str) and isinstance(right, float)) \
                        or isinstance(left, float) and isinstance(right, str):
                    return str(left) + str(right)
                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if float(right) == 0:
                    raise LoxRuntimeError(expr.operator, "Cannot divide by zero.")
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)

        return None

    def visit_grouping_expr(self, expr: GroupingExpr) -> any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
        return None

    def check_number_operand(self, operator: Token, operand: any):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: any, right: any):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def is_truthy(self, obj: any):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def is_equal(self, a: any, b: any):
        return a == b

    def stringify(self, value) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(value)

    def visit_literal_expr(self, expr: LiteralExpr) -> object:
        return expr.value

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def visit_expression_stmt(self, expr: ExpressionStmt) -> None:
        self.evaluate(expr.expression)
        return None

    def visit_print_stmt(self, expr: PrintStmt) -> None:
        value: any = self.evaluate(expr.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        value: any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_variable_expr(self, stmt: VariableExpr):
        return self.environment.get(stmt.name)