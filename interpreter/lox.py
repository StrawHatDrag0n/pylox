import argparse
from typing import List

from interpreter.expr import Expr
from interpreter.interpreter import Interpreter
from interpreter.lox_error_handler import LoxErrorHandler
from interpreter.parser import Parser
from interpreter.lox_token import Token
from interpreter.stmt import Stmt
from tools.ast_printer import ASTPrinter
from interpreter.scanner import Scanner

class Lox:
    @staticmethod
    def main(args: List[str]):
        if len(args) > 1:
            print('Usage: pylox [script]')
            exit(64)
        error_handler = LoxErrorHandler()
        interpreter = Interpreter(error_handler)
        if len(args) == 1:
            Lox.run_file(error_handler, interpreter, args[0])
        else:
            Lox.run_prompt(error_handler, interpreter)

    @staticmethod
    def run_file(error_handler: LoxErrorHandler, interpreter: Interpreter, file_path: str):
        with open(file_path, 'r') as file:
            source_code = file.read()
            Lox.run(error_handler, interpreter, source_code)
            if error_handler.HAS_ERROR:
                exit(65)
            if error_handler.HAS_RUNTIME_ERROR:
                exit(70)

    @staticmethod
    def run_prompt(error_handler: LoxErrorHandler, interpreter: Interpreter,):
        while True:
            print('>', end='')
            line = input()
            if line is None:
                break
            Lox.run(error_handler, interpreter, line)
            error_handler.HAS_ERROR = False

    @staticmethod
    def run(error_handler: LoxErrorHandler, interpreter: Interpreter, source_code):

        scanner: Scanner = Scanner(error_handler, source_code)
        tokens: List[Token] = scanner.scan_tokens()

        parser: Parser = Parser(error_handler, tokens)
        statements: List[Stmt] = parser.parse()
        if error_handler.HAS_ERROR:
            return
        interpreter.interpret(statements)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=False)
    args = parser.parse_args()

    Lox.main([args.file] if args.file else [])