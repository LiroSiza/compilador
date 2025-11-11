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

# Buscar nodo de operación binaria
def find_binop(node, depth=0):
    indent = '  ' * depth
    if hasattr(node, 'type') and node.type == 'operacion_binaria':
        print(f'{indent}Encontrado nodo operacion_binaria:')
        print(f'{indent}  type: {node.type}')
        print(f'{indent}  hasattr value: {hasattr(node, "value")}')
        if hasattr(node, 'value'):
            print(f'{indent}  value: {repr(node.value)}')
        print(f'{indent}  repr(node): {repr(node)}')
        print(f'{indent}  str(node): {str(node)}')
    
    if hasattr(node, 'children'):
        for child in node.children:
            find_binop(child, depth + 1)

print('=== Buscando nodos operacion_binaria ===')
find_binop(annotated_ast)
