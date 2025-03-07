from __future__ import annotations
from typing import List, Any, Optional
import typing

from interpreter.break_exception import BreakException
from interpreter.clock import Clock
from interpreter.environment import Environment
from interpreter.expr import AssignExpr, CallExpr, ExprVisitor, GetExpr, LogicalExpr, SetExpr, SuperExpr, ThisExpr, UnaryExpr, LiteralExpr, GroupingExpr, BinaryExpr, TernaryExpr, Expr, \
    VarExpr
from interpreter.lox_callable import LoxCallable
from interpreter.lox_class import LoxClass
from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.lox_function import LoxFunction
from interpreter.lox_instance import LoxInstance
from interpreter.lox_runtime_error import LoxRuntimeError
from interpreter.lox_token import Token
from interpreter.lox_token_type import TokenType
from interpreter.return_exception import Return
from interpreter.stmt import BreakStmt, ClassStmt, FunctionStmt, IfStmt, ReturnStmt, StmtVisitor, PrintStmt, ExpressionStmt, Stmt, VarStmt, BlockStmt, WhileStmt


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, error_handler: LoxErrorHandler):
        self.error_handler = error_handler
        self.globals = Environment()
        self.environment: Environment = self.globals
        self.locals: dict[Expr, Optional[int]] = dict()

        self.globals.define("clock", Clock())

    def interpret(self, statements: List[Stmt], repl: bool = False) -> None:
        try:
            for stmt in statements:
                value = self.execute(stmt)
                if repl and isinstance(stmt, ExpressionStmt):
                    print(value)
        except LoxRuntimeError as error:
            self.error_handler.runtime_error(error)

    def visit_ternary_expr(self, expr: TernaryExpr) -> Any:
        pass

    def visit_binary_expr(self, expr: BinaryExpr) -> Any:
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)

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
    
    def visit_call_expr(self, expr: CallExpr):
        callee: object = self.evaluate(expr.callee)
        arguments: List[object] = list()
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise RuntimeError("Can only call functions and classes.")
        functionObj: LoxCallable = typing.cast(LoxCallable, callee)
        if len(arguments) != functionObj.arity():
            raise RuntimeError(expr.paren, f"Expected {functionObj.arity()} arguments but got {len(arguments)}.")
        return functionObj.call(self, arguments)

    def visit_get_expr(self, expr: GetExpr):
        obj: Any = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            obj = typing.cast(LoxInstance, obj)
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: GroupingExpr) -> Any:
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

    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def is_truthy(self, obj: Any) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def is_equal(self, a: Any, b: Any) -> bool:
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

    def visit_literal_expr(self, expr: LiteralExpr) -> Any:
        return expr.value

    def visit_logical_expr(self, expr: LogicalExpr) -> Any:
        left: Any = self.evaluate(expr.left)
        
        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: SetExpr):
        obj: Any = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value: Any = self.evaluate(expr.value)
        obj = typing.cast(LoxInstance, obj)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: SuperExpr):
        distance: int = typing.cast(int, self.locals.get(expr, 0))
        superclass: LoxClass = typing.cast(LoxClass, self.environment.get_at(distance, "super"))

        obj : LoxInstance = typing.cast(LoxInstance, self.environment.get_at(distance-1, "this"))

        method: Optional[LoxFunction] = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise LoxRuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")
        return method.bind(obj)

    def visit_this_expr(self, expr: ThisExpr):
        return self.look_up_variable(expr.keyword, expr)

    def visit_while_stmt(self, stmt: WhileStmt):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        except BreakException as e:
            pass
        return None

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        return stmt.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        previous: Environment = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_class_stmt(self, stmt: ClassStmt):
        superclass: Any = None
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(stmt.superclass.name, "Superclass must be a class.")
        
        self.environment.define(stmt.name.lexeme, None)
        
        if stmt.superclass:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods: dict[str, LoxFunction] = dict()
        for method in stmt.methods:
            function_obj : LoxFunction = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function_obj

        klass: LoxClass = LoxClass(stmt.name.lexeme, superclass, methods)
        if stmt.superclass:
            self.environment = typing.cast(Environment, self.environment.enclosing)
        self.environment.assign(stmt.name, klass)
        
        return None

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_expression_stmt(self, expr: ExpressionStmt) -> None:
        return self.evaluate(expr.expression)
    
    def visit_function_stmt(self, stmt: FunctionStmt):
        functionObj = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, functionObj)
        return functionObj 

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elsebranch:
            self.execute(stmt.elsebranch)
        return None

    def visit_print_stmt(self, expr: PrintStmt) -> None:
        value: Any = self.evaluate(expr.expression)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, stmt: ReturnStmt):
        value: object = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        raise Return(value)

    def visit_break_stmt(self, stmt: BreakStmt):
        raise BreakException()

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        value: Any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        if value is None:
            raise LoxRuntimeError(stmt.name, "A variable must be initialized before it can be used.")
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_var_expr(self, expr: VarExpr) -> Any:
        return self.look_up_variable(expr.name, expr)
    
    def look_up_variable(self, name: Token, expr: Expr):
        distance: Optional[int] =  self.locals.get(expr, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    def visit_assign_expr(self, expr: AssignExpr) -> Any:
        value =  self.evaluate(expr.value)
        distance: Optional[int] = self.locals.get(expr, None)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, expr)
        else:
            self.globals.assign(expr.name, value)
        self.environment.assign(expr.name, value)    
        return value
    