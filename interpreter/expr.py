from abc import ABC, abstractmethod
from typing import Any, List, Optional
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

class AssignExpr(Expr):
	def __init__(self, name: Token, value: Expr):
		self.name = name
		self.value = value

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class BinaryExpr(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class CallExpr(Expr):
	def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class GetExpr(Expr):
	def __init__(self, obj: Expr, name: Token):
		self.obj = obj
		self.name = name

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class GroupingExpr(Expr):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class LiteralExpr(Expr):
	def __init__(self, value: Any):
		self.value = value

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class LogicalExpr(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class SetExpr(Expr):
	def __init__(self, obj: Expr, name: Token, value: Expr):
		self.obj = obj
		self.name = name
		self.value = value

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class SuperExpr(Expr):
	def __init__(self, keyword: Token, method: Token):
		self.keyword = keyword
		self.method = method

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class ThisExpr(Expr):
	def __init__(self, keyword: Token):
		self.keyword = keyword

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class UnaryExpr(Expr):
	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class VarExpr(Expr):
	def __init__(self, name: Token):
		self.name = name

	def accept(self, visitor: IExprVisitor):
		return visitor.visit_expr(self)

class ExprVisitor(IExprVisitor):
	def visit_expr(self, expr):
		match expr:
			case TernaryExpr():
				return self.visit_ternary_expr(expr)
			case AssignExpr():
				return self.visit_assign_expr(expr)
			case BinaryExpr():
				return self.visit_binary_expr(expr)
			case CallExpr():
				return self.visit_call_expr(expr)
			case GetExpr():
				return self.visit_get_expr(expr)
			case GroupingExpr():
				return self.visit_grouping_expr(expr)
			case LiteralExpr():
				return self.visit_literal_expr(expr)
			case LogicalExpr():
				return self.visit_logical_expr(expr)
			case SetExpr():
				return self.visit_set_expr(expr)
			case SuperExpr():
				return self.visit_super_expr(expr)
			case ThisExpr():
				return self.visit_this_expr(expr)
			case UnaryExpr():
				return self.visit_unary_expr(expr)
			case VarExpr():
				return self.visit_var_expr(expr)

	@abstractmethod
	def visit_ternary_expr(self, expr: TernaryExpr):
		...

	@abstractmethod
	def visit_assign_expr(self, expr: AssignExpr):
		...

	@abstractmethod
	def visit_binary_expr(self, expr: BinaryExpr):
		...

	@abstractmethod
	def visit_call_expr(self, expr: CallExpr):
		...

	@abstractmethod
	def visit_get_expr(self, expr: GetExpr):
		...

	@abstractmethod
	def visit_grouping_expr(self, expr: GroupingExpr):
		...

	@abstractmethod
	def visit_literal_expr(self, expr: LiteralExpr):
		...

	@abstractmethod
	def visit_logical_expr(self, expr: LogicalExpr):
		...

	@abstractmethod
	def visit_set_expr(self, expr: SetExpr):
		...

	@abstractmethod
	def visit_super_expr(self, expr: SuperExpr):
		...

	@abstractmethod
	def visit_this_expr(self, expr: ThisExpr):
		...

	@abstractmethod
	def visit_unary_expr(self, expr: UnaryExpr):
		...

	@abstractmethod
	def visit_var_expr(self, expr: VarExpr):
		...

