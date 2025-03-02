from typing import List 
from collections import deque
from interpreter.class_type import ClassType
from interpreter.expr import AssignExpr, BinaryExpr, CallExpr, Expr, ExprVisitor, GetExpr, GroupingExpr, LiteralExpr, LogicalExpr, SetExpr, SuperExpr, TernaryExpr, ThisExpr, UnaryExpr, VarExpr
from interpreter.function_type import FunctionType
from interpreter.interpreter import Interpreter
from interpreter.lox_token import Token
from interpreter.stmt import BlockStmt, BreakStmt, ClassStmt, ExpressionStmt, FunctionStmt, IfStmt, PrintStmt, ReturnStmt, Stmt, StmtVisitor, VarStmt, WhileStmt

class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpretor: Interpreter):
        self.interpretor: Interpreter = interpretor
        self.scopes: deque[dict[str, bool]] = deque()
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve(self, statements: List[Stmt] | Stmt | Expr | None):
        if isinstance(statements, List) and all(isinstance(statement, Stmt) for statement in statements):
            for statement in statements:
                self.resolve(statement)
        if isinstance(statements, Stmt):
            statements.accept(self)
        if isinstance(statements, Expr):
            statements.accept(self)

    def begin_scope(self):
        self.scopes.append(dict())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return None
        
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.interpretor.error_handler.error_on_token(name, "Already a variable with this name in this scope.")
        
        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return None
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpretor.resolve(expr, i)
                return None

    def resolve_function(self, func: FunctionStmt, type: FunctionType):
        enclosing_function: FunctionType = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in func.params:
            self.declare(param)
            self.define(param)
        
        self.resolve(func.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_class_stmt(self, stmt: ClassStmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.interpretor.error_handler.error_on_token(stmt.superclass.name, "A class can't inherit from itself.")
        if stmt.superclass:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass:
            self.begin_scope()
            self.scopes[-1]['super'] = True

        self.begin_scope()
        self.scopes[-1]['this'] = True
        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
  
        if stmt.superclass:
            self.end_scope()
        self.end_scope()

        self.current_class = enclosing_class
        return None

    def visit_block_stmt(self, stmt: BlockStmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self.resolve(stmt.expression)
        return None

    def visit_var_stmt(self, stmt: VarStmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        
        self.define(stmt.name)
        return None

    def visit_var_expr(self, expr: VarExpr):
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) == False:
            self.interpretor.error_handler.error_on_token(expr.name, "Can't real local variable in its own initializer.")
        
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_assign_expr(self, expr: AssignExpr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_function_stmt(self, stmt: FunctionStmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def visit_if_stmt(self, stmt: IfStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch) 
        if stmt.elsebranch:
            self.resolve(stmt.elsebranch)
        return None

    def visit_print_stmt(self, stmt: PrintStmt):
        self.resolve(stmt.expression)
        return None

    def visit_return_stmt(self, stmt: ReturnStmt):
        if self.current_function == FunctionType.NONE:
            self.interpretor.error_handler.error_on_token(stmt.keyword, "Can't return from top-level code.")
        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                self.interpretor.error_handler.error_on_token(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)
        return None

    def visit_while_stmt(self, stmt: WhileStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_ternary_expr(self, expr: TernaryExpr):
        self.resolve(expr.condition)
        self.resolve(expr.then_branch)
        self.resolve(expr.then_branch)
        return None

    def visit_binary_expr(self, expr: BinaryExpr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_call_expr(self, expr: CallExpr):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        return None
    
    def visit_get_expr(self, expr: GetExpr):
        self.resolve(expr.obj)
        return None

    def visit_break_stmt(self, stmt: BreakStmt):
        if len(self.scopes) == 0:
            self.interpretor.error_handler.error_on_token(stmt.keyword, "Cannot have 'break' without a scope.")
        return None

    def visit_grouping_expr(self, expr: GroupingExpr):
        self.resolve(expr.expression)
        return None

    def visit_literal_expr(self, expr: LiteralExpr):
        return None

    def visit_logical_expr(self, expr: LogicalExpr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_set_expr(self, expr: SetExpr):
        self.resolve(expr.value)
        self.resolve(expr.obj)
        return None

    def visit_this_expr(self, expr: ThisExpr):
        if self.current_class == ClassType.NONE:
            self.interpretor.error_handler.error_on_token(expr.keyword, "Can't use 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_super_expr(self, expr: SuperExpr):
        if self.current_class == ClassType.NONE:
            self.interpretor.error_handler.error_on_token(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class == ClassType.SUBCLASS:
            self.interpretor.error_handler.error_on_token(expr.keyword, "Can't use 'super' in a class with no superclass.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_unary_expr(self, expr: UnaryExpr):
        self.resolve(expr.right)
        return None