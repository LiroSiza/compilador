from parser import *

class IntermediateCodeGenerator:
    def __init__(self, annotated_ast, symbol_table):
        self.annotated_ast = annotated_ast
        self.symbol_table = symbol_table
        self.instructions = []
        self.next_address = 0
        self.label_counter = 0
        self.temp_vars = {}  # For temporary variables if needed

    def generate_code(self):
        """Generate intermediate P-code from annotated AST"""
        if not self.annotated_ast:
            return []

        self.instructions = []
        self.next_address = 0
        self.label_counter = 0

        # Start with program
        self.generate_program(self.annotated_ast)

        return self.instructions

    def generate_program(self, node):
        """Generate code for program node"""
        if not node:
            return

        # Process declarations and statements
        for child in node.children:
            if hasattr(child, 'type') and child.type == 'lista_declaraciones':
                # Process declaration list children
                for decl_child in child.children:
                    if isinstance(decl_child, VariableDeclarationNode) or (hasattr(decl_child, 'type') and decl_child.type == 'declaracion_variable'):
                        # Declarations don't generate code
                        pass
                    elif hasattr(decl_child, 'type') and decl_child.type == 'lista_sentencias':
                        self.generate_statement_list(decl_child)

    def generate_statement_list(self, node):
        """Generate code for statement list"""
        if not node:
            return

        for child in node.children:
            self.generate_statement(child)

    def generate_statement(self, node):
        """Generate code for individual statement"""
        if not node:
            return

        node_type = node.type if hasattr(node, 'type') else str(type(node).__name__)

        if node_type == 'asignacion' or isinstance(node, AssignmentNode):
            self.generate_assignment(node)
        elif node_type == 'seleccion' or isinstance(node, IfNode):
            self.generate_if(node)
        elif node_type == 'lista_sentencias':
            self.generate_statement_list(node)
        elif isinstance(node, WhileNode):
            self.generate_while(node)
        elif isinstance(node, DoUntilNode):
            self.generate_do_until(node)
        elif isinstance(node, InputNode):
            self.generate_input(node)
        elif isinstance(node, OutputNode):
            self.generate_output(node)

    def generate_assignment(self, node):
        """Generate code for assignment"""
        if len(node.children) >= 2:
            # Generate code for the expression
            self.generate_expression(node.children[1])

            # Store result to variable
            var_node = node.children[0]
            if isinstance(var_node, IdentifierNode):
                entry = self.symbol_table.lookup(var_node.value)
                if entry:
                    self.add_instruction(f"sto {entry.address}", f"almacena resultado en variable '{var_node.value}' (dirección {entry.address})")

    def generate_expression(self, node):
        """Generate code for expression"""
        if not node:
            return

        node_type = node.type if hasattr(node, 'type') else str(type(node).__name__)

        if node_type == 'operacion_binaria' or isinstance(node, BinaryOpNode):
            self.generate_binary_op(node)
        elif node_type == 'ID' or isinstance(node, IdentifierNode):
            self.generate_identifier_load(node)
        elif node_type == 'NUM' or isinstance(node, NumberNode):
            self.generate_number_load(node)
        elif isinstance(node, BooleanNode):
            self.generate_boolean_load(node)
        elif isinstance(node, StringNode):
            self.generate_string_load(node)

    def generate_binary_op(self, node):
        """Generate code for binary operation"""
        if len(node.children) >= 2:
            # Generate code for left operand
            self.generate_expression(node.children[0])

            # Generate code for right operand
            self.generate_expression(node.children[1])

            # Apply operation
            op = node.value
            if op == '+':
                self.add_instruction("add", "suma los dos valores superiores de la pila")
            elif op == '-':
                self.add_instruction("sub", "resta los dos valores superiores de la pila")
            elif op == '*':
                self.add_instruction("mul", "multiplica los dos valores superiores de la pila")
            elif op == '/':
                self.add_instruction("div", "divide los dos valores superiores de la pila")
            elif op == '^':
                self.add_instruction("pow", "eleva el penúltimo valor a la potencia del último valor de la pila")
            elif op == '<':
                self.add_instruction("les", "comparación menor que")
            elif op == '<=':
                self.add_instruction("leq", "comparación menor o igual que")
            elif op == '>':
                self.add_instruction("grt", "comparación mayor que")
            elif op == '>=':
                self.add_instruction("geq", "comparación mayor o igual que")
            elif op == '==':
                self.add_instruction("equ", "comparación igual que")
            elif op == '!=':
                self.add_instruction("neq", "comparación no igual que")
            elif op == '&&':
                self.add_instruction("and", "operación lógica AND")
            elif op == '||':
                self.add_instruction("or", "operación lógica OR")

    def generate_identifier_load(self, node):
        """Generate code to load identifier value"""
        entry = self.symbol_table.lookup(node.value)
        if entry:
            self.add_instruction(f"lod {entry.address}", f"carga variable '{node.value}' desde dirección {entry.address}")

    def generate_number_load(self, node):
        """Generate code to load number constant"""
        if hasattr(node, 'semantic_type'):
            if node.semantic_type == 'int':
                self.add_instruction(f"ldc {node.value}", f"carga constante entero {node.value}")
            elif node.semantic_type == 'float':
                self.add_instruction(f"ldc {node.value}", f"carga constante flotante {node.value}")
        else:
            # Fallback: determine type from value
            if '.' in str(node.value):
                self.add_instruction(f"ldc {node.value}", f"carga constante flotante {node.value}")
            else:
                self.add_instruction(f"ldc {node.value}", f"carga constante entero {node.value}")

    def generate_boolean_load(self, node):
        """Generate code to load boolean constant"""
        value = 1 if node.value else 0
        self.add_instruction(f"ldc {value}", f"carga constante booleano {node.value}")

    def generate_string_load(self, node):
        """Generate code to load string constant"""
        # Remove quotes from the string value
        string_value = node.value.strip('"')
        self.add_instruction(f"lds \"{string_value}\"", f"carga constante cadena \"{string_value}\"")

    def generate_if(self, node):
        """Generate code for if statement"""
        if len(node.children) >= 2:
            # Generate condition
            self.generate_expression(node.children[0])

            # False jump to else label
            else_label = self.new_label()
            self.add_instruction(f"fjp {else_label}", f"si condición es falsa, salta a etiqueta {else_label}")

            # Generate then branch
            self.generate_statement(node.children[1])

            if len(node.children) > 2:
                # Jump to end after then branch
                end_label = self.new_label()
                self.add_instruction(f"ujp {end_label}", f"salta a fin de estructura if")

                # Else branch
                self.add_instruction(f"lab {else_label}", f"etiqueta rama else")
                self.generate_statement(node.children[2])

                # End label
                self.add_instruction(f"lab {end_label}", f"etiqueta fin de estructura if")
            else:
                # No else branch
                self.add_instruction(f"lab {else_label}", f"etiqueta fin de estructura if")

    def generate_while(self, node):
        """Generate code for while loop"""
        if len(node.children) >= 2:
            # Start label
            start_label = self.new_label()
            self.place_label(start_label)

            # Generate condition
            self.generate_expression(node.children[0])

            # False jump to end
            end_label = self.new_label()
            self.add_instruction(f"fjp {end_label}", f"si condición es falsa, salta a fin del bucle")

            # Generate body
            self.generate_statement(node.children[1])

            # Jump back to start
            self.add_instruction(f"ujp {start_label}", f"salta a inicio del bucle while")

            # End label
            self.place_label(end_label)

    def generate_do_until(self, node):
        """Generate code for do-until loop"""
        if len(node.children) >= 2:
            # Start label
            start_label = self.new_label()
            self.place_label(start_label)

            # Generate body
            self.generate_statement(node.children[0])

            # Generate condition
            self.generate_expression(node.children[1])

            # False jump back to start (continue loop if condition is false)
            self.add_instruction(f"fjp {start_label}", f"si condición es falsa, continúa el bucle")

    def generate_input(self, node):
        """Generate code for input statement"""
        if node.children:
            var_node = node.children[0]
            if isinstance(var_node, IdentifierNode):
                # Read value
                self.add_instruction("cin", "lee valor desde entrada estándar")

                # Store to variable
                entry = self.symbol_table.lookup(var_node.value)
                if entry:
                    self.add_instruction(f"sto {entry.address}", f"almacena valor leído en variable '{var_node.value}' (dirección {entry.address})")

    def generate_output(self, node):
        """Generate code for output statement"""
        for child in node.children:
            # Generate expression to output
            self.generate_expression(child)

            # Write to output
            self.add_instruction("cout", "escribe valor en salida estándar")

    def add_instruction(self, instruction, description):
        """Add an instruction to the list"""
        self.instructions.append({
            'address': self.next_address,
            'instruction': instruction,
            'description': description
        })
        self.next_address += 1

    def place_label(self, label):
        """Place a label at the current address"""
        self.instructions.append({
            'address': self.next_address,
            'instruction': f"lab {label}",
            'description': f"etiqueta {label}"
        })
        self.next_address += 1

    def new_label(self):
        """Generate a new unique label"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def get_code_table(self):
        """Return the generated code as a formatted table"""
        if not self.instructions:
            return "No se generó código intermedio"

        result = "Código Intermedio (P-code):\n"
        result += "-" * 80 + "\n"
        result += f"{'Dir':<5} {'Instrucción':<20} {'Descripción'}\n"
        result += "-" * 80 + "\n"

        for instr in self.instructions:
            result += f"{instr['address']:<5} {instr['instruction']:<20} {instr['description']}\n"

        return result