from abc import ABC, abstractmethod
from interpreter.lox_token import Token

class IExprVisitor(ABC):
	@abstractmethod
	def visit_expr(self, expr):
		...

class Expr(ABC):
	@abstractmethod
	def accept(self, visitor: IExprVisitor):
		...

class TernaryExpr(Expr):
	def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class BinaryExpr(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class GroupingExpr(Expr):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class LiteralExpr(Expr):
	def __init__(self, value: any):
		self.value = value

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class UnaryExpr(Expr):
	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class VariableExpr(Expr):
	def __init__(self, name: Token):
		self.name = name

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class ExprVisitor(IExprVisitor):
	def visit_expr(self, expr):
		match expr:
			case TernaryExpr():
				return self.visit_ternary_expr(expr)
			case BinaryExpr():
				return self.visit_binary_expr(expr)
			case GroupingExpr():
				return self.visit_grouping_expr(expr)
			case LiteralExpr():
				return self.visit_literal_expr(expr)
			case UnaryExpr():
				return self.visit_unary_expr(expr)
			case VariableExpr():
				return self.visit_variable_expr(expr)

	@abstractmethod
	def visit_ternary_expr(self, expr: TernaryExpr):
		...

	@abstractmethod
	def visit_binary_expr(self, expr: BinaryExpr):
		...

	@abstractmethod
	def visit_grouping_expr(self, expr: GroupingExpr):
		...

	@abstractmethod
	def visit_literal_expr(self, expr: LiteralExpr):
		...

	@abstractmethod
	def visit_unary_expr(self, expr: UnaryExpr):
		...

	@abstractmethod
	def visit_variable_expr(self, expr: VariableExpr):
		...

