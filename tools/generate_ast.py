import argparse
from typing import List
import os
import re

class GenerateAST:

    @staticmethod
    def main(args: List[str]):
        if len(args) != 1:
            print(f"Usage: generate_ast [output directory]")
            exit(64)
        output_dir = args[0]
        GenerateAST.define_ast(output_dir, "Expr", [
            "Ternary    -   condition: Expr, then_branch: Expr, else_branch: Expr",
            "Assign     -   name: Token, value: Expr",
            "Binary     -   left: Expr, operator: Token, right: Expr",
            "Call       -   callee: Optional[Expr], paren: Token, arguments: List[Expr]",
            "Get        -   obj: Expr, name: Token",
            "Grouping   -   expression: Expr",
            "Literal    -   value: Any",
            "Logical    -   left: Expr, operator: Token, right: Expr",
            "Set        -   obj: Expr, name: Token, value: Expr",
            "Super      -   keyword: Token, method: Token",
            "This       -   keyword: Token",
            "Unary      -   operator: Token, right: Expr",
            "Var        -   name: Token" # VariableExpr
        ])

        GenerateAST.define_ast(output_dir, "Stmt", [
            "Block          -   statements: List[Stmt]",
            "Expression     -   expression: Expr",
            "Function       -   name: Optional[Token], params: List[Token], body: List[Stmt]",
            "Class          -   name: Token, superclass: Optional[VarExpr], methods: List[FunctionStmt]",
            "If             -   condition: Expr, thenBranch: Stmt, elsebranch: Optional[Stmt]",
            "Print          -   expression: Expr",
            "Return         -   keyword: Token, value: Optional[Expr]",
            "Var            -   name: Token, initializer: Optional[Expr]",
            "While          -   condition: Expr, body: Stmt",
            "Break          -   keyword: Token"
        ], ["from interpreter.expr import Expr, VarExpr"])


    @staticmethod
    def get_snake_case(text: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

    @staticmethod
    def define_ast(output_dir: str, base_class, class_definitions: List[str], imps: List[str]=[]):
        with open(os.path.join(output_dir, f'{base_class.lower()}.py'), 'w+') as file:
            file.write('from abc import ABC, abstractmethod\n')
            file.write('from typing import Any, List, Optional\n')
            file.write('from interpreter.lox_token import Token\n')
            for imp in imps:
                file.write(imp + '\n')
            file.write('\n')

            file.write(f'class I{base_class}Visitor(ABC):\n')
            file.write(f'\t@abstractmethod\n')
            file.write(f'\tdef visit_{base_class.lower()}(self, expr):\n')
            file.write('\t\t...\n')
            file.write('\n')

            file.write(f'class {base_class}(ABC):\n')
            file.write(f'\t@abstractmethod\n')
            file.write(f'\tdef accept(self, visitor: I{base_class}Visitor):\n')
            file.write('\t\t...\n')
            file.write('\n')

            for class_definition in class_definitions:
                class_parts = class_definition.split('-')
                class_name = class_parts[0].strip() + base_class
                fields = class_parts[1].strip()
                file.write(f'class {class_name}({base_class}):\n')
                if fields:
                    file.write(f'\tdef __init__(self, {fields}):\n')
                    for field in fields.split(','):
                        field = field.split(':')[0].strip()
                        file.write(f'\t\tself.{field} = {field}\n')
                else:
                    file.write(f'\tdef __init__(self):\n')
                    file.write('\t\tpass\n')
                file.write('\n')
                file.write(f'\tdef accept(self, visitor: I{base_class}Visitor):\n')
                file.write(f'\t\treturn visitor.visit_{base_class.lower()}(self)\n')
                file.write('\n')

            file.write(f'class {base_class}Visitor(I{base_class}Visitor):\n')
            file.write(f'\tdef visit_{base_class.lower()}(self, expr):\n')
            file.write('\t\tmatch expr:\n')
            for class_definition in class_definitions:
                class_parts = class_definition.split('-')
                class_name = class_parts[0].strip() + base_class
                file.write(f'\t\t\tcase {class_name}():\n')
                file.write(f'\t\t\t\treturn self.visit_{GenerateAST.get_snake_case(class_name)}(expr)\n')
            file.write('\n')
            for class_definition in class_definitions:
                class_parts = class_definition.split('-')
                class_name = class_parts[0].strip()
                file.write(f'\t@abstractmethod\n')
                file.write(f'\tdef visit_{GenerateAST.get_snake_case(class_name)}_{GenerateAST.get_snake_case(base_class)}(self, {base_class.lower()}: {class_name}{base_class}):\n')
                file.write('\t\t...\n')
                file.write('\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-od', '--output_directory', required=False)
    args = parser.parse_args()
    GenerateAST.main([args.output_directory] if args.output_directory else [])