from parser import *

class SymbolTableEntry:
    def __init__(self, name, var_type, scope='global', line=None, column=None):
        self.name = name
        self.type = var_type
        self.scope = scope
        self.declaration_line = line  # Línea de declaración
        self.declaration_column = column
        self.lines = [line] if line is not None else []  # Todas las líneas donde aparece
        self.memory_address = None  # For future use

    def add_reference(self, line):
        """Agrega una línea donde se referencia el símbolo"""
        if line not in self.lines:
            self.lines.append(line)

    def __str__(self):
        lines_str = ', '.join(map(str, sorted(self.lines)))
        return f"Nombre: {self.name}, Tipo: {self.type}, Ámbito: {self.scope}, Líneas: {lines_str}"

class SymbolTable:
    def __init__(self):
        self.table = {}
        self.errors = []

    def insert(self, name, var_type, line=None, column=None):
        if name in self.table:
            self.errors.append(f"Variable '{name}' ya declarada en línea {line}, columna {column}")
            return False
        entry = SymbolTableEntry(name, var_type, 'global', line, column)
        self.table[name] = entry
        return True

    def add_reference(self, name, line):
        """Agrega una referencia a un símbolo existente"""
        entry = self.table.get(name)
        if entry:
            entry.add_reference(line)

    def lookup(self, name):
        return self.table.get(name, None)

    def get_all_entries(self):
        return list(self.table.values())

    def __str__(self):
        if not self.table:
            return "Tabla de símbolos vacía"
        result = "Tabla de Símbolos:\n"
        result += "-" * 100 + "\n"
        result += f"{'Nombre':<15} {'Tipo':<10} {'Ámbito':<10} {'Líneas':<20}\n"
        result += "-" * 100 + "\n"
        for entry in self.table.values():
            lines_str = ', '.join(map(str, sorted(entry.lines)))
            result += f"{entry.name:<15} {entry.type:<10} {entry.scope:<10} {lines_str:<20}\n"
        return result

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.errors = []
        self.annotated_ast = None

    def analyze(self):
        """Main analysis method"""
        if not self.ast:
            self.errors.append("No hay AST para analizar")
            return None, self.errors

        # First pass: build symbol table from declarations
        self.build_symbol_table(self.ast)

        # Second pass: type checking and attribute propagation
        self.annotated_ast = self.annotate_types(self.ast)

        return self.annotated_ast, self.errors + self.symbol_table.errors

    def build_symbol_table(self, node):
        """Build symbol table from variable declarations"""
        if not node:
            return

        if isinstance(node, VariableDeclarationNode):
            # Extract type from the first child (TypeNode)
            type_node = node.children[0] if node.children else None
            var_type = type_node.value if type_node else "unknown"

            # Extract identifiers from remaining children
            for child in node.children[1:]:
                if isinstance(child, IdentifierNode):
                    self.symbol_table.insert(child.value, var_type, child.line, child.column)

        # Recursively process children
        for child in node.children:
            self.build_symbol_table(child)

    def annotate_types(self, node):
        """Annotate AST with type information"""
        if not node:
            return node

        # Clone the node to avoid modifying the original
        annotated_node = ASTNode(node.type, node.value, node.line, node.column)
        annotated_node.children = []

        # Process based on node type
        if isinstance(node, VariableDeclarationNode):
            annotated_node = self.annotate_variable_declaration(node)
        elif isinstance(node, AssignmentNode):
            annotated_node = self.annotate_assignment(node)
        elif isinstance(node, BinaryOpNode):
            annotated_node = self.annotate_binary_op(node)
        elif isinstance(node, IfNode):
            annotated_node = self.annotate_if(node)
        elif isinstance(node, WhileNode):
            annotated_node = self.annotate_while(node)
        elif isinstance(node, DoUntilNode):
            annotated_node = self.annotate_do_until(node)
        elif isinstance(node, InputNode):
            annotated_node = self.annotate_input(node)
        elif isinstance(node, OutputNode):
            annotated_node = self.annotate_output(node)
        elif isinstance(node, IdentifierNode):
            annotated_node = self.annotate_identifier(node)
        elif isinstance(node, NumberNode):
            annotated_node = self.annotate_number(node)
        elif isinstance(node, BooleanNode):
            annotated_node = self.annotate_boolean(node)
        elif isinstance(node, UnaryOpNode):
            annotated_node = self.annotate_unary_op(node)
        else:
            # For other nodes, just copy children with annotation
            for child in node.children:
                annotated_child = self.annotate_types(child)
                if annotated_child:
                    annotated_node.add_child(annotated_child)

        return annotated_node

    def annotate_variable_declaration(self, node):
        """Annotate variable declaration"""
        annotated = VariableDeclarationNode(None, [])
        annotated.line = node.line
        annotated.column = node.column

        # Copy type node
        if node.children:
            type_node = node.children[0]
            annotated_type = TypeNode(type_node.value, type_node.line, type_node.column)
            annotated.add_child(annotated_type)

            # Annotate identifiers
            for child in node.children[1:]:
                if isinstance(child, IdentifierNode):
                    annotated_id = IdentifierNode(child.value, child.line, child.column)
                    # Add type attribute
                    annotated_id.semantic_type = type_node.value
                    annotated.add_child(annotated_id)

        return annotated

    def annotate_assignment(self, node):
        """Annotate assignment with type checking"""
        annotated = AssignmentNode(None, None)
        annotated.line = node.line
        annotated.column = node.column

        if len(node.children) >= 2:
            id_node = node.children[0]
            expr_node = node.children[1]

            # Annotate identifier
            annotated_id = self.annotate_identifier(id_node)
            annotated.add_child(annotated_id)

            # Annotate expression
            annotated_expr = self.annotate_types(expr_node)
            annotated.add_child(annotated_expr)

            # Type checking
            if hasattr(annotated_id, 'semantic_type') and hasattr(annotated_expr, 'semantic_type'):
                id_type = annotated_id.semantic_type
                expr_type = annotated_expr.semantic_type

                if not self.types_compatible(id_type, expr_type):
                    self.errors.append(f"Tipos incompatibles en asignación: '{id_type}' = '{expr_type}' en línea {node.line}, columna {node.column}")
                else:
                    # Add type to assignment node
                    annotated.semantic_type = id_type

        return annotated

    def annotate_binary_op(self, node):
        """Annotate binary operation with type checking"""
        annotated = BinaryOpNode(node.value, None, None)
        annotated.line = node.line
        annotated.column = node.column

        if len(node.children) >= 2:
            left = self.annotate_types(node.children[0])
            right = self.annotate_types(node.children[1])

            annotated.add_child(left)
            annotated.add_child(right)

            # Type checking for binary operations
            if hasattr(left, 'semantic_type') and hasattr(right, 'semantic_type'):
                left_type = left.semantic_type
                right_type = right.semantic_type

                result_type = self.get_binary_op_result_type(node.value, left_type, right_type)
                if result_type:
                    annotated.semantic_type = result_type
                else:
                    self.errors.append(f"Operación '{node.value}' no válida entre tipos '{left_type}' y '{right_type}' en línea {node.line}, columna {node.column}")

        return annotated

    def annotate_identifier(self, node):
        """Annotate identifier with type lookup"""
        annotated = IdentifierNode(node.value, node.line, node.column)

        # Look up type in symbol table
        entry = self.symbol_table.lookup(node.value)
        if entry:
            annotated.semantic_type = entry.type
            # Register this line as a reference to the symbol
            self.symbol_table.add_reference(node.value, node.line)
        else:
            self.errors.append(f"Variable '{node.value}' no declarada en línea {node.line}, columna {node.column}")
            annotated.semantic_type = "unknown"

        return annotated

    def annotate_number(self, node):
        """Annotate number literal"""
        annotated = NumberNode(node.value, node.line, node.column)

        # Determine type based on value
        try:
            if '.' in str(node.value):
                annotated.semantic_type = "float"
            else:
                annotated.semantic_type = "int"
        except:
            annotated.semantic_type = "int"

        return annotated

    def annotate_boolean(self, node):
        """Annotate boolean literal"""
        annotated = BooleanNode(node.value, node.line, node.column)
        annotated.semantic_type = "bool"
        return annotated

    def annotate_if(self, node):
        """Annotate if statement"""
        annotated = IfNode(None, None, None)
        annotated.line = node.line
        annotated.column = node.column

        if node.children:
            # Condition should be boolean
            condition = self.annotate_types(node.children[0])
            annotated.add_child(condition)

            if hasattr(condition, 'semantic_type') and condition.semantic_type != "bool":
                self.errors.append(f"Condición del if debe ser booleana, encontrado '{condition.semantic_type}' en línea {node.line}, columna {node.column}")

            # Then statement
            if len(node.children) > 1:
                then_stmt = self.annotate_types(node.children[1])
                annotated.add_child(then_stmt)

            # Else statement (optional)
            if len(node.children) > 2:
                else_stmt = self.annotate_types(node.children[2])
                annotated.add_child(else_stmt)

        return annotated

    def annotate_while(self, node):
        """Annotate while statement"""
        annotated = WhileNode(None, None)
        annotated.line = node.line
        annotated.column = node.column

        if len(node.children) >= 2:
            condition = self.annotate_types(node.children[0])
            annotated.add_child(condition)

            if hasattr(condition, 'semantic_type') and condition.semantic_type != "bool":
                self.errors.append(f"Condición del while debe ser booleana, encontrado '{condition.semantic_type}' en línea {node.line}, columna {node.column}")

            body = self.annotate_types(node.children[1])
            annotated.add_child(body)

        return annotated

    def annotate_do_until(self, node):
        """Annotate do-until statement"""
        annotated = DoUntilNode(None, None)
        annotated.line = node.line
        annotated.column = node.column

        if len(node.children) >= 2:
            body = self.annotate_types(node.children[0])
            annotated.add_child(body)

            condition = self.annotate_types(node.children[1])
            annotated.add_child(condition)

            if hasattr(condition, 'semantic_type') and condition.semantic_type != "bool":
                self.errors.append(f"Condición del do-until debe ser booleana, encontrado '{condition.semantic_type}' en línea {node.line}, columna {node.column}")

        return annotated

    def annotate_input(self, node):
        """Annotate input statement"""
        annotated = InputNode(None)
        annotated.line = node.line
        annotated.column = node.column

        if node.children:
            id_node = self.annotate_identifier(node.children[0])
            annotated.add_child(id_node)

        return annotated

    def annotate_output(self, node):
        """Annotate output statement"""
        annotated = OutputNode(None)
        annotated.line = node.line
        annotated.column = node.column

        if node.children:
            expr = self.annotate_types(node.children[0])
            annotated.add_child(expr)

        return annotated

    def annotate_unary_op(self, node):
        """Annotate unary operation"""
        annotated = UnaryOpNode(node.value, None)
        annotated.line = node.line
        annotated.column = node.column

        if node.children:
            operand = self.annotate_types(node.children[0])
            annotated.add_child(operand)

            if hasattr(operand, 'semantic_type'):
                if node.value == "!":
                    if operand.semantic_type == "bool":
                        annotated.semantic_type = "bool"
                    else:
                        self.errors.append(f"Operador '!' requiere operando booleano, encontrado '{operand.semantic_type}' en línea {node.line}, columna {node.column}")
                else:
                    annotated.semantic_type = operand.semantic_type

        return annotated

    def types_compatible(self, type1, type2):
        """Check if two types are compatible for assignment"""
        if type1 == type2:
            return True

        # Allow int to float conversion
        if type1 == "float" and type2 == "int":
            return True

        return False

    def get_binary_op_result_type(self, op, type1, type2):
        """Get result type for binary operation"""
        # Arithmetic operations
        if op in ['+', '-', '*', '/']:
            if type1 in ['int', 'float'] and type2 in ['int', 'float']:
                return 'float' if 'float' in [type1, type2] else 'int'

        # Comparison operations
        if op in ['<', '<=', '>', '>=', '==', '!=']:
            if type1 in ['int', 'float'] and type2 in ['int', 'float']:
                return 'bool'

        # Logical operations
        if op in ['&&', '||']:
            if type1 == 'bool' and type2 == 'bool':
                return 'bool'

        return None