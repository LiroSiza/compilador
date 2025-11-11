import sys
sys.path.append('src')
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

code = '''main {
    int x;
    x = 3 + 5;
}'''

# Análisis léxico
lexer = Lexer()
tokens, _ = lexer.tokenize(code)

# Parsing
parser = Parser(tokens)
ast, _ = parser.parse()

# Análisis semántico
analyzer = SemanticAnalyzer(ast)
annotated_ast, _ = analyzer.analyze()

# Simular lo que hace _get_node_display_text
def get_display_text(node):
    if hasattr(node, 'type'):
        node_type = node.type
    else:
        node_type = str(type(node).__name__)
        
    # Check for constant value first
    if hasattr(node, 'constant_value') and node.constant_value is not None:
        # Special case for identifiers: show name and constant value
        if node_type == 'ID' and hasattr(node, 'value'):
            return f"{node_type}({node.value}, {node.constant_value})"
        return f"{node_type}({node.constant_value})"
        
    if hasattr(node, 'value') and node.value is not None:
        # For operacion_binaria, show both symbol and descriptive name
        if node_type == 'operacion_binaria':
            op_names = {
                '+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE',
                '%': 'MODULO', '^': 'POWER', '==': 'EQUAL', '!=': 'NOT_EQUAL',
                '<': 'LESS_THAN', '<=': 'LESS_EQUAL', '>': 'GREATER_THAN', '>=': 'GREATER_EQUAL',
                '&&': 'AND', '||': 'OR'
            }
            op_name = op_names.get(node.value, node.value)
            return f"operacion_binaria({node.value} → {op_name})"
        return f"{node_type}({node.value})"
    return node_type

# Buscar nodo de operación binaria
def find_and_display(node, depth=0):
    indent = '  ' * depth
    if hasattr(node, 'type') and node.type == 'operacion_binaria':
        display_text = get_display_text(node)
        semantic_type = getattr(node, 'semantic_type', '')
        print(f'{indent}Display text: {display_text}')
        print(f'{indent}Semantic type: {semantic_type}')
        print(f'{indent}Line: {node.line}')
        print(f'{indent}Column: {node.column}')
        print(f'{indent}Values tuple: ({semantic_type!r}, {""!r}, {node.line or ""!r}, {node.column or ""!r})')
    
    if hasattr(node, 'children'):
        for child in node.children:
            find_and_display(child, depth + 1)

print('=== Simulando visualización en UI ===')
find_and_display(annotated_ast)
