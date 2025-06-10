#!/usr/bin/env python3

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser

def test_expanded_tree():
    # Test code with various constructs
    test_code = """
main {
    int a, b;
    a = 5 + 3 * 2;
    b++;
    a--;
    if a > b then
        cout << a;
    end
}
"""

    print("Testing expanded AST tree functionality...")
    print("Code to parse:")
    print(test_code)
    print("\n" + "="*50 + "\n")

    # Tokenize
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(test_code)
    
    if lex_errors:
        print("Lexical errors:")
        for error in lex_errors:
            print(f"  {error}")
        return

    # Parse
    parser = Parser(tokens)
    ast_root, parse_errors = parser.parse()
    
    if parse_errors:
        print("Parse errors:")
        for error in parse_errors:
            print(f"  {error}")
        return

    print("AST Structure (will be fully expanded in GUI):")
    print_ast(ast_root, 0)

def print_ast(node, level):
    """Print AST structure in a tree-like format"""
    if not node:
        return
    
    indent = "  " * level
    node_info = f"{indent}{node.type}"
    
    if hasattr(node, 'value') and node.value is not None:
        node_info += f" ({node.value})"
    
    if hasattr(node, 'line') and node.line is not None:
        node_info += f" [Line: {node.line}"
        if hasattr(node, 'column') and node.column is not None:
            node_info += f", Col: {node.column}"
        node_info += "]"
    
    print(node_info)
    
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            print_ast(child, level + 1)

if __name__ == "__main__":
    test_expanded_tree()
