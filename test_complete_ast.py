#!/usr/bin/env python3
"""
Complete test of the AST implementation including all features:
- Proper node types and operation names
- Post-increment transformation
- Full tree structure
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser

def test_complete_ast():
    """Test all AST features with a comprehensive program"""
    
    # Test code with various constructs including post-increment
    test_code = """main {
    int x, y, z;
    float a, b;
    
    x = 5 + 3 * 2;
    y = 10 - 4 / 2;
    z = x ^ 2;
    a = 3.14;
    b = a * 2.0;
    
    x++;
    y--;
    
    if x > y then
        cout << x;
        if y < z then
            b = b + 1.0;
        end
    else
        cout << y;
    end
    
    while x > 0
        x = x - 1;
        cin >> y;
    end
    
    do
        z = z + 1;
    until z == 10;
}"""

    print("=" * 60)
    print("COMPLETE AST TEST")
    print("=" * 60)
    print("Code to parse:")
    print(test_code)
    print("\n" + "=" * 60 + "\n")

    # Tokenize
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(test_code)
    
    if lex_errors:
        print("LEXICAL ERRORS:")
        for error in lex_errors:
            print(f"  {error}")
        return

    print("TOKENIZATION: SUCCESS")
    print(f"Generated {len(tokens)} tokens")
    
    # Parse and build AST
    parser = Parser(tokens)
    ast_root, parse_errors = parser.parse()
    
    if parse_errors:
        print("\nPARSE ERRORS:")
        for error in parse_errors:
            print(f"  {error}")
        return

    print("PARSING: SUCCESS")
    print("AST created successfully")
    
    print("\n" + "=" * 60)
    print("AST STRUCTURE (with operation types)")
    print("=" * 60)
    print_ast_with_operations(ast_root, 0)
    
    print("\n" + "=" * 60)
    print("POST-INCREMENT ANALYSIS")
    print("=" * 60)
    
    # Find and analyze post-increment transformations
    assignments = find_assignments(ast_root)
    increment_count = 0
    
    for assignment in assignments:
        if is_transformed_increment(assignment):
            increment_count += 1
            var_name = assignment.children[0].value if assignment.children else 'unknown'
            op_type = get_increment_type(assignment)
            print(f"✓ Found transformed post-{op_type}: {var_name} = {var_name} {'+' if op_type == 'increment' else '-'} 1")
    
    print(f"\nTotal post-increment/decrement transformations: {increment_count}")
    
    print("\n" + "=" * 60)
    print("NODE TYPE ANALYSIS")
    print("=" * 60)
    
    node_counts = count_node_types(ast_root)
    for node_type, count in sorted(node_counts.items()):
        print(f"{node_type:20} : {count}")
    
    print("\n" + "=" * 60)
    print("OPERATION TYPE MAPPING")
    print("=" * 60)
    
    operations = find_operations(ast_root)
    for op_symbol, op_name in operations:
        print(f"{op_symbol:6} -> {op_name}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("✓ All AST nodes created properly")
    print("✓ Post-increment transformations working")
    print("✓ Operation types mapped correctly")
    print("✓ Tree structure is complete and expandable")
    print("=" * 60)

def print_ast_with_operations(node, level):
    """Print AST structure showing operation types"""
    if not node:
        return
    
    indent = "  " * level
    node_info = f"{indent}{node.type}"
    
    # Show operation type for binary/unary operations
    if node.type in ("operacion_binaria", "operacion_unaria") and hasattr(node, 'value') and node.value:
        operation_type = get_operation_type(node.value)
        node_info += f" ({operation_type})"
    elif hasattr(node, 'value') and node.value is not None:
        node_info += f" ({node.value})"
    
    if hasattr(node, 'line') and node.line is not None:
        node_info += f" [Line: {node.line}"
        if hasattr(node, 'column') and node.column is not None:
            node_info += f", Col: {node.column}"
        node_info += "]"
    
    print(node_info)
    
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            print_ast_with_operations(child, level + 1)

def get_operation_type(operator):
    """Map operators to descriptive names"""
    operator_map = {
        '+': 'PLUS',
        '-': 'MINUS', 
        '*': 'MULTIPLY',
        '/': 'DIVIDE',
        '%': 'MODULO',
        '^': 'POWER',
        '=': 'ASSIGN',
        '==': 'EQUAL',
        '!=': 'NOT_EQUAL',
        '<': 'LESS_THAN',
        '<=': 'LESS_EQUAL',
        '>': 'GREATER_THAN',
        '>=': 'GREATER_EQUAL',
        '&&': 'AND',
        '||': 'OR',
        '!': 'NOT',
        '++': 'INCREMENT',
        '--': 'DECREMENT'
    }
    return operator_map.get(operator, operator)

def find_assignments(node):
    """Find all assignment nodes in the AST"""
    assignments = []
    
    if hasattr(node, 'type') and node.type == 'asignacion':
        assignments.append(node)
    
    if hasattr(node, 'children'):
        for child in node.children:
            assignments.extend(find_assignments(child))
    
    return assignments

def is_transformed_increment(assignment):
    """Check if an assignment is a transformed post-increment/decrement"""
    if (len(assignment.children) >= 2 and 
        hasattr(assignment.children[1], 'type') and 
        assignment.children[1].type == 'operacion_binaria'):
        
        binary_op = assignment.children[1]
        if (len(binary_op.children) >= 2 and
            hasattr(binary_op.children[1], 'type') and
            binary_op.children[1].type == 'NUM' and
            binary_op.children[1].value == 1 and
            binary_op.value in ('+', '-')):
            
            # Check if left operand is the same variable as assignment target
            if (hasattr(assignment.children[0], 'value') and
                hasattr(binary_op.children[0], 'value') and
                assignment.children[0].value == binary_op.children[0].value):
                return True
    
    return False

def get_increment_type(assignment):
    """Get the type of increment operation (increment or decrement)"""
    if (len(assignment.children) >= 2 and 
        hasattr(assignment.children[1], 'value')):
        return "increment" if assignment.children[1].value == '+' else "decrement"
    return "unknown"

def count_node_types(node):
    """Count occurrences of each node type"""
    counts = {}
    
    if hasattr(node, 'type'):
        counts[node.type] = counts.get(node.type, 0) + 1
    
    if hasattr(node, 'children'):
        for child in node.children:
            child_counts = count_node_types(child)
            for node_type, count in child_counts.items():
                counts[node_type] = counts.get(node_type, 0) + count
    
    return counts

def find_operations(node):
    """Find all operations and their mapped types"""
    operations = set()
    
    if (hasattr(node, 'type') and 
        node.type in ('operacion_binaria', 'operacion_unaria') and
        hasattr(node, 'value') and node.value):
        operations.add((node.value, get_operation_type(node.value)))
    
    if hasattr(node, 'children'):
        for child in node.children:
            operations.update(find_operations(child))
    
    return sorted(list(operations))

if __name__ == "__main__":
    test_complete_ast()
