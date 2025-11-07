#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

def test_semantic_ui():
    # Load testSemantica.txt
    try:
        with open('testSemantica.txt', 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print("testSemantica.txt not found")
        return

    print("=== TESTING SEMANTIC ANALYSIS ===")
    print(f"Code length: {len(code)}")

    # Lexical analysis
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(code)
    print(f"Tokens: {len(tokens)}, Lex errors: {len(lex_errors)}")

    # Syntax analysis
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()
    print(f"AST: {ast is not None}, Parse errors: {len(parse_errors)}")

    if ast:
        # Semantic analysis
        semantic_analyzer = SemanticAnalyzer(ast)
        annotated_ast, semantic_errors = semantic_analyzer.analyze()

        print(f"Annotated AST: {annotated_ast is not None}")
        print(f"Semantic errors: {len(semantic_errors)}")
        print(f"Symbol table entries: {len(semantic_analyzer.symbol_table.table)}")

        # Check if attributes are set
        print(f"Has last_annotated_ast: {annotated_ast is not None}")
        print(f"Has symbol_table: {semantic_analyzer.symbol_table is not None}")

        print("\n=== SYMBOL TABLE ===")
        print(semantic_analyzer.symbol_table)

        print("\n=== SEMANTIC ERRORS ===")
        for error in semantic_errors:
            print(f"  {error}")

if __name__ == "__main__":
    test_semantic_ui()