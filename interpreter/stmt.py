from abc import ABC, abstractmethod
from typing import Any, List, Optional
from interpreter.lox_token import Token
from interpreter.expr import Expr, VarExpr

class IStmtVisitor(ABC):
	@abstractmethod
	def visit_stmt(self, expr):
		...

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: IStmtVisitor):
		...

class BlockStmt(Stmt):
	def __init__(self, statements: List[Stmt]):
		self.statements = statements

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class ExpressionStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class FunctionStmt(Stmt):
	def __init__(self, name: Optional[Token], params: List[Token], body: List[Stmt]):
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class ClassStmt(Stmt):
	def __init__(self, name: Token, superclass: Optional[VarExpr], methods: List[FunctionStmt]):
		self.name = name
		self.superclass = superclass
		self.methods = methods

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class IfStmt(Stmt):
	def __init__(self, condition: Expr, thenBranch: Stmt, elsebranch: Optional[Stmt]):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elsebranch = elsebranch

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class PrintStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class ReturnStmt(Stmt):
	def __init__(self, keyword: Token, value: Optional[Expr]):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class VarStmt(Stmt):
	def __init__(self, name: Token, initializer: Optional[Expr]):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class WhileStmt(Stmt):
	def __init__(self, condition: Expr, body: Stmt):
		self.condition = condition
		self.body = body

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class BreakStmt(Stmt):
	def __init__(self, keyword: Token):
		self.keyword = keyword

	def accept(self, visitor: IStmtVisitor):
		return visitor.visit_stmt(self)

class StmtVisitor(IStmtVisitor):
	def visit_stmt(self, expr):
		match expr:
			case BlockStmt():
				return self.visit_block_stmt(expr)
			case ExpressionStmt():
				return self.visit_expression_stmt(expr)
			case FunctionStmt():
				return self.visit_function_stmt(expr)
			case ClassStmt():
				return self.visit_class_stmt(expr)
			case IfStmt():
				return self.visit_if_stmt(expr)
			case PrintStmt():
				return self.visit_print_stmt(expr)
			case ReturnStmt():
				return self.visit_return_stmt(expr)
			case VarStmt():
				return self.visit_var_stmt(expr)
			case WhileStmt():
				return self.visit_while_stmt(expr)
			case BreakStmt():
				return self.visit_break_stmt(expr)

	@abstractmethod
	def visit_block_stmt(self, stmt: BlockStmt):
		...

	@abstractmethod
	def visit_expression_stmt(self, stmt: ExpressionStmt):
		...

	@abstractmethod
	def visit_function_stmt(self, stmt: FunctionStmt):
		...

	@abstractmethod
	def visit_class_stmt(self, stmt: ClassStmt):
		...

	@abstractmethod
	def visit_if_stmt(self, stmt: IfStmt):
		...

	@abstractmethod
	def visit_print_stmt(self, stmt: PrintStmt):
		...

	@abstractmethod
	def visit_return_stmt(self, stmt: ReturnStmt):
		...

	@abstractmethod
	def visit_var_stmt(self, stmt: VarStmt):
		...

	@abstractmethod
	def visit_while_stmt(self, stmt: WhileStmt):
		...

	@abstractmethod
	def visit_break_stmt(self, stmt: BreakStmt):
		...

