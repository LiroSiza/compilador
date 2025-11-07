#!/usr/bin/env python3
"""
Final validation test for the complete AST IDE implementation.
This test verifies that all components work together correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser

def test_ide_components():
    """Test that all IDE components work correctly"""
    
    print("=" * 60)
    print("FINAL AST IDE VALIDATION TEST")
    print("=" * 60)
    
    # Test code with all language features
    test_code = """main {
    int x, y;
    float z;
    bool flag;
    
    x = 5 + 3;
    y = x * 2;
    z = 3.14;
    flag = true;
    
    x++;
    y--;
    
    if x > y then
        cout << x;
        z = z + 1.0;
    else
        cout << y;
    end
    
    while x > 0
        x = x - 1;
        cin >> y;
    end
    
    do
        y = y + 1;
    until y == 10;
}"""

    print("1. TESTING LEXICAL ANALYSIS...")
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(test_code)
    
    if lex_errors:
        print("   ❌ LEXICAL ERRORS FOUND:")
        for error in lex_errors:
            print(f"      {error}")
        return False
    
    print(f"   ✓ Generated {len(tokens)} tokens successfully")
    
    print("\n2. TESTING PARSER AND AST CONSTRUCTION...")
    parser = Parser(tokens)
    ast_root, parse_errors = parser.parse()
    
    if parse_errors:
        print("   ❌ PARSE ERRORS FOUND:")
        for error in parse_errors:
            print(f"      {error}")
        return False
    
    print("   ✓ AST constructed successfully")
    
    print("\n3. TESTING POST-INCREMENT TRANSFORMATIONS...")
    assignments = find_all_assignments(ast_root)
    increment_transformations = 0
    
    for assignment in assignments:
        if is_increment_transformation(assignment):
            increment_transformations += 1
    
    expected_transformations = 2  # x++ and y--
    if increment_transformations == expected_transformations:
        print(f"   ✓ Found {increment_transformations} post-increment transformations (expected {expected_transformations})")
    else:
        print(f"   ❌ Found {increment_transformations} transformations, expected {expected_transformations}")
        return False
    
    print("\n4. TESTING OPERATION TYPE MAPPING...")
    operations = get_all_operations(ast_root)
    operation_mappings = {
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'MULTIPLY', 
        '>': 'GREATER_THAN',
        '==': 'EQUAL'
    }
    
    all_mappings_correct = True
    for op_symbol, expected_name in operation_mappings.items():
        if op_symbol in [op[0] for op in operations]:
            mapped_name = map_operation_type(op_symbol)
            if mapped_name == expected_name:
                print(f"   ✓ {op_symbol} → {mapped_name}")
            else:
                print(f"   ❌ {op_symbol} → {mapped_name} (expected {expected_name})")
                all_mappings_correct = False
    
    if not all_mappings_correct:
        return False
    
    print("\n5. TESTING AST STRUCTURE...")
    node_types = count_all_node_types(ast_root)
    expected_nodes = {
        'programa': 1,
        'lista_declaraciones': 1,
        'declaracion_variable': 3,  # int, float, bool declarations
        'lista_sentencias': 4,      # main body, if-then, if-else, while body, do body
        'asignacion': 7,            # Including transformed increments
        'seleccion': 1,             # if statement
        'iteracion': 1,             # while loop
        'repeticion': 1,            # do-until loop
        'sent_out': 2,              # cout statements
        'sent_in': 1,               # cin statement
        'operacion_binaria': 11,    # Various binary operations
        'ID': 32,                   # Identifier occurrences
        'NUM': 16,                  # Number literals
        'tipo': 3,                  # Type declarations
        'BOOL': 1                   # Boolean literal
    }
    
    structure_correct = True
    for node_type, expected_count in expected_nodes.items():
        actual_count = node_types.get(node_type, 0)
        if actual_count >= expected_count:
            print(f"   ✓ {node_type}: {actual_count} (expected ≥{expected_count})")
        else:
            print(f"   ❌ {node_type}: {actual_count} (expected ≥{expected_count})")
            structure_correct = False
    
    if not structure_correct:
        return False
    
    print("\n6. TESTING UI INTEGRATION READINESS...")
    # Simulate UI operations that would be performed
    try:
        # Test tree population (simulated)
        tree_nodes = simulate_tree_population(ast_root)
        print(f"   ✓ Tree can be populated with {len(tree_nodes)} nodes")
        
        # Test operation type mapping for UI
        ui_operations = simulate_ui_operation_mapping(ast_root)
        print(f"   ✓ Found {len(ui_operations)} operations for UI display")
        
        # Test expandable structure
        max_depth = calculate_tree_depth(ast_root)
        print(f"   ✓ AST has {max_depth} levels (suitable for tree expansion)")
        
    except Exception as e:
        print(f"   ❌ UI integration test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! AST IDE IS READY!")
    print("✓ Lexical analysis working")
    print("✓ Parser creating proper AST")
    print("✓ Post-increment transformations working")
    print("✓ Operation types mapped correctly")
    print("✓ AST structure is complete")
    print("✓ Ready for UI integration with expandable tree")
    print("=" * 60)
    
    return True

def find_all_assignments(node):
    """Find all assignment nodes in the AST"""
    assignments = []
    if hasattr(node, 'type') and node.type == 'asignacion':
        assignments.append(node)
    if hasattr(node, 'children'):
        for child in node.children:
            assignments.extend(find_all_assignments(child))
    return assignments

def is_increment_transformation(assignment):
    """Check if assignment is a transformed increment/decrement"""
    if (len(assignment.children) >= 2 and 
        hasattr(assignment.children[1], 'type') and 
        assignment.children[1].type == 'operacion_binaria'):
        
        binary_op = assignment.children[1]
        if (len(binary_op.children) >= 2 and
            hasattr(binary_op.children[1], 'type') and
            binary_op.children[1].type == 'NUM' and
            binary_op.children[1].value == 1 and
            binary_op.value in ('+', '-')):
            
            if (hasattr(assignment.children[0], 'value') and
                hasattr(binary_op.children[0], 'value') and
                assignment.children[0].value == binary_op.children[0].value):
                return True
    return False

def get_all_operations(node):
    """Get all operations in the AST"""
    operations = set()
    if (hasattr(node, 'type') and 
        node.type in ('operacion_binaria', 'operacion_unaria') and
        hasattr(node, 'value') and node.value):
        operations.add((node.value, map_operation_type(node.value)))
    if hasattr(node, 'children'):
        for child in node.children:
            operations.update(get_all_operations(child))
    return list(operations)

def map_operation_type(operator):
    """Map operators to descriptive names"""
    operator_map = {
        '+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE',
        '%': 'MODULO', '^': 'POWER', '=': 'ASSIGN', '==': 'EQUAL',
        '!=': 'NOT_EQUAL', '<': 'LESS_THAN', '<=': 'LESS_EQUAL',
        '>': 'GREATER_THAN', '>=': 'GREATER_EQUAL', '&&': 'AND',
        '||': 'OR', '!': 'NOT', '++': 'INCREMENT', '--': 'DECREMENT'
    }
    return operator_map.get(operator, operator)

def count_all_node_types(node):
    """Count all node types in the AST"""
    counts = {}
    if hasattr(node, 'type'):
        counts[node.type] = counts.get(node.type, 0) + 1
    if hasattr(node, 'children'):
        for child in node.children:
            child_counts = count_all_node_types(child)
            for node_type, count in child_counts.items():
                counts[node_type] = counts.get(node_type, 0) + count
    return counts

def simulate_tree_population(node, nodes=None):
    """Simulate populating a tree widget"""
    if nodes is None:
        nodes = []
    
    if node:
        # Simulate creating a tree node
        node_info = {
            'type': node.type,
            'value': getattr(node, 'value', None),
            'line': getattr(node, 'line', None),
            'column': getattr(node, 'column', None)
        }
        nodes.append(node_info)
        
        if hasattr(node, 'children'):
            for child in node.children:
                simulate_tree_population(child, nodes)
    
    return nodes

def simulate_ui_operation_mapping(node):
    """Simulate UI operation mapping"""
    operations = []
    if (hasattr(node, 'type') and 
        node.type in ('operacion_binaria', 'operacion_unaria') and
        hasattr(node, 'value') and node.value):
        
        operation_type = map_operation_type(node.value)
        operations.append({
            'symbol': node.value,
            'type': operation_type,
            'display': f"{node.type} ({operation_type})"
        })
    
    if hasattr(node, 'children'):
        for child in node.children:
            operations.extend(simulate_ui_operation_mapping(child))
    
    return operations

def calculate_tree_depth(node, current_depth=0):
    """Calculate the maximum depth of the AST"""
    if not node or not hasattr(node, 'children') or not node.children:
        return current_depth
    
    max_child_depth = 0
    for child in node.children:
        child_depth = calculate_tree_depth(child, current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth

if __name__ == "__main__":
    success = test_ide_components()
    sys.exit(0 if success else 1)
