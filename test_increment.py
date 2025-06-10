#!/usr/bin/env python3
"""
Test script to verify that post-increment operations are correctly transformed
into assignment operations in the AST.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser

def print_ast(node, indent=0):
    """Recursively print the AST structure"""
    if not node:
        return
    
    prefix = "  " * indent
    node_info = f"{prefix}{node.type}"
    
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
            print_ast(child, indent + 1)

def test_post_increment():
    """Test post-increment transformation"""
    
    # Test code with post-increment
    test_code = """main {
    int a;
    a++;
    a--;
}"""
    
    print("Testing post-increment transformation:")
    print("=" * 50)
    print("Code:")
    print(test_code)
    print("=" * 50)
    
    # Tokenize
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(test_code)
    
    if lex_errors:
        print("Lexical errors:")
        for error in lex_errors:
            print(f"  {error}")
        return
    
    print("Tokens:")
    for token in tokens:
        print(f"  {token}")
    print("=" * 50)
    
    # Parse
    parser = Parser(tokens)
    ast_root, parse_errors = parser.parse()
    
    if parse_errors:
        print("Parse errors:")
        for error in parse_errors:
            print(f"  {error}")
        return
    
    print("AST Structure:")
    print_ast(ast_root)
    print("=" * 50)
    
    # Verify that a++ was transformed to assignment
    def find_assignments(node, assignments=None):
        if assignments is None:
            assignments = []
        
        if hasattr(node, 'type') and node.type == 'asignacion':
            assignments.append(node)
        
        if hasattr(node, 'children'):
            for child in node.children:
                find_assignments(child, assignments)
        
        return assignments
    
    assignments = find_assignments(ast_root)
    print(f"Found {len(assignments)} assignment(s):")
    
    for i, assignment in enumerate(assignments, 1):
        print(f"\nAssignment {i}:")
        print_ast(assignment, 1)
        
        # Check if it's a transformed increment/decrement
        if (len(assignment.children) >= 2 and 
            hasattr(assignment.children[1], 'type') and 
            assignment.children[1].type == 'operacion_binaria'):
            
            binary_op = assignment.children[1]
            if (len(binary_op.children) >= 2 and
                hasattr(binary_op.children[1], 'type') and
                binary_op.children[1].type == 'NUM' and
                binary_op.children[1].value == 1):
                
                op_type = "increment" if binary_op.value == '+' else "decrement"
                var_name = assignment.children[0].value if hasattr(assignment.children[0], 'value') else 'unknown'
                print(f"    -> This is a transformed post-{op_type} of variable '{var_name}'")

if __name__ == "__main__":
    test_post_increment()
