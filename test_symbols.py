#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

def test_symbol_table():
    # Load testSemantica.txt
    try:
        with open('testSemantica.txt', 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print("testSemantica.txt not found, using simple test")
        code = """main {
    int x, y;
    float z;
    x = 5;
}"""

    print("Code length:", len(code))
    print("First 200 chars:", repr(code[:200]))
    print()

    # Lexical analysis
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(code)
    print(f"Tokens: {len(tokens)}")
    print()

    # Syntax analysis
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()
    print(f"Parse errors: {parse_errors}")
    print()

    if ast:
        print("AST Structure:")
        def print_ast(node, depth=0):
            indent = "  " * depth
            print(f"{indent}{node}")
            for child in node.children:
                print_ast(child, depth + 1)
        print_ast(ast)
        print()

        # Test full semantic analysis
        print("=== FULL SEMANTIC ANALYSIS ===")
        semantic_analyzer = SemanticAnalyzer(ast)
        annotated_ast, semantic_errors = semantic_analyzer.analyze()

        print("Symbol Table:")
        print(semantic_analyzer.symbol_table)
        print()

        print("Semantic Errors:")
        for error in semantic_errors:
            print(f"  {error}")
        print()

        if annotated_ast:
            print("Annotated AST Structure:")
            def print_annotated_ast(node, depth=0):
                indent = "  " * depth
                semantic_type = getattr(node, 'semantic_type', 'NO_TYPE')
                print(f"{indent}{node} [type: {semantic_type}]")
                for child in node.children:
                    print_annotated_ast(child, depth + 1)
            print_annotated_ast(annotated_ast)
        else:
            print("No annotated AST returned")

if __name__ == "__main__":
    test_symbol_table()