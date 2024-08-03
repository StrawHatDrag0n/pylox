from abc import ABC, abstractmethod
from interpreter.lox_token import Token
from interpreter.expr import Expr

class IStmtVisitor(ABC):
	@abstractmethod
	def visit_stmt(self, expr):
		...

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: IStmtVisitor):
		...

class ExpressionStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class PrintStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class VarStmt(Stmt):
	def __init__(self, name: Token, initializer: Expr):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class StmtVisitor(IStmtVisitor):
	def visit_stmt(self, expr):
		match expr:
			case ExpressionStmt():
				return self.visit_expression_stmt(expr)
			case PrintStmt():
				return self.visit_print_stmt(expr)
			case VarStmt():
				return self.visit_var_stmt(expr)

	@abstractmethod
	def visit_expression_stmt(self, stmt: ExpressionStmt):
		...

	@abstractmethod
	def visit_print_stmt(self, stmt: PrintStmt):
		...

	@abstractmethod
	def visit_var_stmt(self, stmt: VarStmt):
		...

