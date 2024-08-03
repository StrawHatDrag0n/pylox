
from interpreter.expr import *
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType


class ASTPrinter(ExprVisitor):

    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_ternary_expr(self, expr: TernaryExpr):
        return self.parenthesize("conditional", expr.condition, expr.branch1, expr.branch2)

    def visit_binary_expr(self, expr: BinaryExpr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: GroupingExpr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: LiteralExpr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: UnaryExpr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs):
        result = [f"({name}"]
        for expr in exprs:
            result.append(expr.accept(self))
        result.append(")")
        return " ".join(result)

if __name__ == '__main__':
    expression = BinaryExpr(
        UnaryExpr(
            Token(TokenType.MINUS, "-", None, 1),
            LiteralExpr(123)),
        Token(TokenType.STAR, "*", None, 1),
        GroupingExpr(
            LiteralExpr(45.67)))
    print(ASTPrinter().print(expression))