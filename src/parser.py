from lexer import Token

# AST Node Classes
class ASTNode:
    def __init__(self, type_name, value=None, line=None, column=None):
        self.type = type_name
        self.value = value
        self.line = line
        self.column = column
        self.children = []
    
    def add_child(self, child):
        if child:
            self.children.append(child)
    
    def __repr__(self):
        if self.value:
            return f"{self.type}({self.value})"
        return f"{self.type}"

class ProgramNode(ASTNode):
    def __init__(self):
        super().__init__("programa")

class DeclarationListNode(ASTNode):
    def __init__(self):
        super().__init__("lista_declaraciones")

class VariableDeclarationNode(ASTNode):
    def __init__(self, type_node, identifiers):
        super().__init__("declaracion_variable")
        self.add_child(type_node)
        for id_node in identifiers:
            self.add_child(id_node)

class TypeNode(ASTNode):
    def __init__(self, type_name, line=None, column=None):
        super().__init__("tipo", type_name, line, column)

class IdentifierNode(ASTNode):
    def __init__(self, name, line=None, column=None):
        super().__init__("ID", name, line, column)

class StatementListNode(ASTNode):
    def __init__(self):
        super().__init__("lista_sentencias")

class AssignmentNode(ASTNode):
    def __init__(self, identifier, expression):
        super().__init__("asignacion")
        self.add_child(identifier)
        self.add_child(expression)

class IfNode(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt=None):
        super().__init__("seleccion")
        self.add_child(condition)
        self.add_child(then_stmt)
        if else_stmt:
            self.add_child(else_stmt)

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        super().__init__("iteracion")
        self.add_child(condition)
        self.add_child(body)

class DoUntilNode(ASTNode):
    def __init__(self, body, condition):
        super().__init__("repeticion")
        self.add_child(body)
        self.add_child(condition)

class InputNode(ASTNode):
    def __init__(self, identifier):
        super().__init__("sent_in")
        self.add_child(identifier)

class OutputNode(ASTNode):
    def __init__(self, expression):
        super().__init__("sent_out")
        self.add_child(expression)

class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right):
        super().__init__("operacion_binaria", operator)
        self.add_child(left)
        self.add_child(right)

class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand):
        super().__init__("operacion_unaria", operator)
        self.add_child(operand)

class NumberNode(ASTNode):
    def __init__(self, value, line=None, column=None):
        super().__init__("NUM", value, line, column)

class BooleanNode(ASTNode):
    def __init__(self, value, line=None, column=None):
        super().__init__("BOOL", value, line, column)

class PostIncrementNode(ASTNode):
    def __init__(self, identifier, operator):
        super().__init__("post_increment")
        self.add_child(identifier)
        self.add_child(ASTNode("operador", operator))

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.ast = None

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def match(self, token_type, value=None):
        tok = self.current()
        if tok and tok.type == token_type and (value is None or tok.value == value):
            self.advance()
            return tok
        # Error recovery: record and continue
        if tok:
            expected = value if value else token_type
            self.errors.append(f"Se esperaba '{expected}' en línea {tok.line}, col {tok.column}")
        else:
            self.errors.append(f"Se esperaba '{value or token_type}' al final de entrada")
        return None

    def peek(self):
        """Return next token without consuming"""
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None

    def parse(self):
        self.ast = self.parse_program()
        if self.current():
            tok = self.current()
            self.errors.append(f"Token inesperado '{tok.value}' en línea {tok.line}, col {tok.column}")
        return self.ast, self.errors    # Grammar methods
    def parse_program(self):
        # program → main { lista_declaracion }
        program = ProgramNode()
        if not self.match(4, 'main'):
            return program
        if not self.match(7, '{'):
            return program
        decl_list = self.parse_lista_declaracion()
        program.add_child(decl_list)
        self.match(7, '}')
        return program

    def parse_lista_declaracion(self):
        # lista_declaracion → declaracion { declaracion }
        decl_list = DeclarationListNode()
        while True:
            tok = self.current()
            if not tok:
                break
            # starts with type or statement or id
            if (tok.type == 4 and tok.value in ('int', 'float', 'bool')) or \
               (tok.type == 4 and tok.value in ('if', 'while', 'do', 'cin', 'cout')) or \
               tok.type == 2:
                decl = self.parse_declaracion()
                decl_list.add_child(decl)
            else:
                break
        return decl_list

    def parse_declaracion(self):
        # declaracion → declaracion_variable | lista_sentencias
        tok = self.current()
        if tok and tok.type == 4 and tok.value in ('int', 'float', 'bool'):
            return self.parse_declaracion_variable()
        else:
            return self.parse_lista_sentencias()

    def parse_declaracion_variable(self):
        # tipo identificador ;
        type_node = self.parse_tipo()
        identifiers = self.parse_identificador()
        self.match(7, ';')
        return VariableDeclarationNode(type_node, identifiers)

    def parse_tipo(self):
        tok = self.current()
        if tok and tok.type == 4 and tok.value in ('int', 'float', 'bool'):
            self.advance()
            return TypeNode(tok.value, tok.line, tok.column)
        else:
            if tok:
                self.errors.append(f"Tipo inválido '{tok.value}' en línea {tok.line}, col {tok.column}")
            else:
                self.errors.append("Se esperaba tipo al final de entrada")
            return TypeNode("unknown")

    def parse_identificador(self):
        identifiers = []
        tok = self.current()
        if tok and tok.type == 2:
            identifiers.append(IdentifierNode(tok.value, tok.line, tok.column))
            self.advance()
            while True:
                tok2 = self.current()
                if tok2 and tok2.type == 7 and tok2.value == ',':
                    self.advance()
                    if self.current() and self.current().type == 2:
                        tok3 = self.current()
                        identifiers.append(IdentifierNode(tok3.value, tok3.line, tok3.column))
                        self.advance()
                    else:
                        tok3 = self.current()
                        if tok3:
                            self.errors.append(f"Se esperaba identificador después de ',' en línea {tok3.line}, col {tok3.column}")
                        break
                else:
                    break
        else:
            if tok:
                self.errors.append(f"Se esperaba identificador en línea {tok.line}, col {tok.column}")
            else:
                self.errors.append("Se esperaba identificador al final de entrada")
        return identifiers

    def parse_lista_sentencias(self):
        # lista_sentencias → { sentencia }
        stmt_list = StatementListNode()
        while True:
            tok = self.current()
            if not tok:
                break
            if tok.type == 4 and tok.value in ('if', 'while', 'do', 'cin', 'cout') or tok.type == 2:
                stmt = self.parse_sentencia()
                stmt_list.add_child(stmt)
            else:
                break
        return stmt_list

    def parse_sentencia(self):
        tok = self.current()
        if not tok:
            return None
        if tok.type == 4 and tok.value == 'if':
            return self.parse_seleccion()
        elif tok.type == 4 and tok.value == 'while':
            return self.parse_iteracion()
        elif tok.type == 4 and tok.value == 'do':
            return self.parse_repeticion()
        elif tok.type == 4 and tok.value == 'cin':
            return self.parse_sent_in()
        elif tok.type == 4 and tok.value == 'cout':
            return self.parse_sent_out()
        elif tok.type == 2:
            # check for post-increment/decrement
            nxt = self.peek()
            if nxt and nxt.type == 5 and nxt.value in ('++','--'):
                return self.parse_post_increment()
            else:
                return self.parse_asignacion()
        else:
            self.errors.append(f"Sentencia inválida '{tok.value}' en línea {tok.line}, col {tok.column}")
            self.advance()
            return None

    def parse_post_increment(self):
        """Parse post-increment/decrement statement: id++ ; or id-- ;"""
        """Transforms a++ into assignment: a = a + 1"""
        # Consume id
        id_tok = self.match(2)
        id_node = IdentifierNode(id_tok.value, id_tok.line, id_tok.column) if id_tok else None
        
        # Consume ++ or --
        tok = self.current()
        op_value = None
        if tok and tok.type == 5 and tok.value in ('++','--'):
            op_value = tok.value
            self.advance()
        else:
            if tok:
                self.errors.append(f"Se esperaba '++' o '--' en línea {tok.line}, col {tok.column}")
        
        # Expect semicolon
        self.match(7, ';')
        
        # Create assignment node: a = a + 1 (or a = a - 1 for --)
        if id_node and op_value:
            # Create a copy of the identifier for the right side of the assignment
            right_id_node = IdentifierNode(id_node.value, id_node.line, id_node.column)
            
            # Create the number node (1)
            one_node = NumberNode(1, id_node.line, id_node.column)
            
            # Determine the operator (+ for ++, - for --)
            binary_op = '+' if op_value == '++' else '-'
            
            # Create binary operation: a + 1 or a - 1
            binary_expr = BinaryOpNode(binary_op, right_id_node, one_node)
            
            # Create assignment: a = (a + 1) or a = (a - 1)
            return AssignmentNode(id_node, binary_expr)
        
        # Fallback if something went wrong
        return PostIncrementNode(id_node, op_value)
        """Parse post-increment/decrement statement: id++ ; or id-- ;"""
        """Transforms a++ into assignment: a = a + 1"""
        # Consume id
        id_tok = self.match(2)
        id_node = IdentifierNode(id_tok.value, id_tok.line, id_tok.column) if id_tok else None
        
        # Consume ++ or --
        tok = self.current()
        op_value = None
        if tok and tok.type == 5 and tok.value in ('++','--'):
            op_value = tok.value
            self.advance()
        else:
            if tok:
                self.errors.append(f"Se esperaba '++' o '--' en línea {tok.line}, col {tok.column}")
        
        # Expect semicolon
        self.match(7, ';')
        
        # Create assignment node: a = a + 1 (or a = a - 1 for --)
        if id_node and op_value:
            # Create a copy of the identifier for the right side of the assignment
            right_id_node = IdentifierNode(id_node.value, id_node.line, id_node.column)
            
            # Create the number node (1)
            one_node = NumberNode(1, id_node.line, id_node.column)
            
            # Determine the operator (+ for ++, - for --)
            binary_op = '+' if op_value == '++' else '-'
            
            # Create binary operation: a + 1 or a - 1
            binary_expr = BinaryOpNode(binary_op, right_id_node, one_node)
            
            # Create assignment: a = (a + 1) or a = (a - 1)
            return AssignmentNode(id_node, binary_expr)
        
        # Fallback if something went wrong
        return PostIncrementNode(id_node, op_value)

    def parse_asignacion(self):
        # id = sent_expresion
        id_tok = self.match(2)
        id_node = IdentifierNode(id_tok.value, id_tok.line, id_tok.column) if id_tok else None
        self.match(8, '=')
        expr = self.parse_sent_expresion()
        return AssignmentNode(id_node, expr)

    def parse_sent_expresion(self):
        # expresion ; | ;
        tok = self.current()
        if tok and tok.type == 7 and tok.value == ';':
            self.advance()
            return None
        else:
            expr = self.parse_expresion()
            self.match(7, ';')
            return expr

    def parse_seleccion(self):
        # if expresion then lista_sentencias [ else lista_sentencias ] end
        self.match(4, 'if')
        condition = self.parse_expresion()
        self.match(4, 'then')
        then_stmt = self.parse_lista_sentencias()
        else_stmt = None
        tok = self.current()
        if tok and tok.type == 4 and tok.value == 'else':
            self.advance()
            else_stmt = self.parse_lista_sentencias()
        self.match(4, 'end')
        return IfNode(condition, then_stmt, else_stmt)

    def parse_iteracion(self):
        # while expresion lista_sentencias end
        self.match(4, 'while')
        condition = self.parse_expresion()
        body = self.parse_lista_sentencias()
        self.match(4, 'end')
        return WhileNode(condition, body)

    def parse_repeticion(self):
        # do lista_sentencias until expresion ;
        self.match(4, 'do')
        body = self.parse_lista_sentencias()
        self.match(4, 'until')
        condition = self.parse_expresion()
        # require semicolon after until
        self.match(7, ';')
        return DoUntilNode(body, condition)

    def parse_sent_in(self):
        # cin >> id ;
        self.match(4, 'cin')
        # expect two '>' symbols
        for _ in range(2):
            tok = self.current()
            if tok and tok.type == 6 and tok.value == '>':
                self.advance()
            else:
                if tok:
                    self.errors.append(f"Se esperaba '>' en línea {tok.line}, col {tok.column}")
        id_tok = self.match(2)
        id_node = IdentifierNode(id_tok.value, id_tok.line, id_tok.column) if id_tok else None
        self.match(7, ';')
        return InputNode(id_node)

    def parse_sent_out(self):
        # cout << salida
        self.match(4, 'cout')
        # expect two '<'
        for _ in range(2):
            tok = self.current()
            if tok and tok.type == 6 and tok.value == '<':
                self.advance()
            else:
                if tok:
                    self.errors.append(f"Se esperaba '<' en línea {tok.line}, col {tok.column}")
        # Parse expression until semicolon
        expr = self.parse_expresion()
        # optional semicolon
        if self.current() and self.current().type == 7 and self.current().value == ';':
            self.advance()
        return OutputNode(expr)

    def parse_expresion(self):
        # parse simple expression
        left = self.parse_expresion_simple()
        # handle relational operators
        tok = self.current()
        if tok and tok.type == 6 and tok.value in ('<','<=','>','>=','==','!='):
            op = tok.value
            self.advance()
            right = self.parse_expresion_simple()
            left = BinaryOpNode(op, left, right)
        # handle logical AND/OR operators
        tok = self.current()
        while tok and tok.type == 6 and tok.value in ('&&','||'):
            op = tok.value
            self.advance()
            right = self.parse_expresion_simple()
            left = BinaryOpNode(op, left, right)
            tok = self.current()
        return left

    def parse_expresion_simple(self):
        left = self.parse_termino()
        while True:
            tok = self.current()
            if tok and tok.type == 5 and tok.value in ('+','-'):
                op = tok.value
                self.advance()
                right = self.parse_termino()
                left = BinaryOpNode(op, left, right)
            else:
                break
        return left

    def parse_termino(self):
        left = self.parse_factor()
        while True:
            tok = self.current()
            if tok and tok.type == 5 and tok.value in ('*','/','%'):
                op = tok.value
                self.advance()
                right = self.parse_factor()
                left = BinaryOpNode(op, left, right)
            else:
                break
        return left

    def parse_factor(self):
        left = self.parse_componente()
        tok = self.current()
        if tok and tok.type == 5 and tok.value == '^':
            op = tok.value
            self.advance()
            right = self.parse_componente()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_componente(self):
        tok = self.current()
        if not tok:
            return None
        if tok.type == 7 and tok.value == '(':
            self.advance()
            expr = self.parse_expresion()
            self.match(7, ')')
            return expr
        elif tok.type in (1,10):  # número
            self.advance()
            return NumberNode(tok.value, tok.line, tok.column)
        elif tok.type == 2:  # id
            self.advance()
            return IdentifierNode(tok.value, tok.line, tok.column)
        elif tok.type == 4 and tok.value in ('true','false'):  # boolean
            self.advance()
            return BooleanNode(tok.value, tok.line, tok.column)
        elif tok.type == 6 and tok.value in ('!'):
            op = tok.value
            self.advance()
            operand = self.parse_componente()
            return UnaryOpNode(op, operand)
        else:
            # unknown
            self.errors.append(f"Componente inválido '{tok.value}' en línea {tok.line}, col {tok.column}")
            self.advance()
            return None
