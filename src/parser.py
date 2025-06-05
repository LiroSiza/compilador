from lexer import Token

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def match(self, token_type, value=None):
        tok = self.current()
        if tok and tok.type == token_type and (value is None or tok.value == value):
            self.advance()
            return True
        # Error recovery: record and continue
        if tok:
            expected = value if value else token_type
            self.errors.append(f"Se esperaba '{expected}' en línea {tok.line}, col {tok.column}")
        else:
            self.errors.append(f"Se esperaba '{value or token_type}' al final de entrada")
        return False

    def peek(self):
        """Return next token without consuming"""
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None

    def parse(self):
        self.parse_program()
        if self.current():
            tok = self.current()
            self.errors.append(f"Token inesperado '{tok.value}' en línea {tok.line}, col {tok.column}")
        return self.errors

    # Grammar methods
    def parse_program(self):
        # program → main { lista_declaracion }
        if not self.match(4, 'main'):
            return
        if not self.match(7, '{'):
            return
        self.parse_lista_declaracion()
        self.match(7, '}')

    def parse_lista_declaracion(self):
        # lista_declaracion → declaracion { declaracion }
        while True:
            tok = self.current()
            if not tok:
                break
            # starts with type or statement or id
            if (tok.type == 4 and tok.value in ('int', 'float', 'bool')) or \
               (tok.type == 4 and tok.value in ('if', 'while', 'do', 'cin', 'cout')) or \
               tok.type == 2:
                self.parse_declaracion()
            else:
                break

    def parse_declaracion(self):
        # declaracion → declaracion_variable | lista_sentencias
        tok = self.current()
        if tok and tok.type == 4 and tok.value in ('int', 'float', 'bool'):
            self.parse_declaracion_variable()
        else:
            self.parse_lista_sentencias()

    def parse_declaracion_variable(self):
        # tipo identificador ;
        self.parse_tipo()
        self.parse_identificador()
        self.match(7, ';')

    def parse_tipo(self):
        tok = self.current()
        if tok and tok.type == 4 and tok.value in ('int', 'float', 'bool'):
            self.advance()
        else:
            if tok:
                self.errors.append(f"Tipo inválido '{tok.value}' en línea {tok.line}, col {tok.column}")
            else:
                self.errors.append("Se esperaba tipo al final de entrada")

    def parse_identificador(self):
        tok = self.current()
        if tok and tok.type == 2:
            self.advance()
            while True:
                tok2 = self.current()
                if tok2 and tok2.type == 7 and tok2.value == ',':
                    self.advance()
                    if self.current() and self.current().type == 2:
                        self.advance()
                    else:
                        tok3 = self.current()
                        self.errors.append(f"Se esperaba identificador después de ',' en línea {tok3.line}, col {tok3.column}")
                        break
                else:
                    break
        else:
            if tok:
                self.errors.append(f"Se esperaba identificador en línea {tok.line}, col {tok.column}")
            else:
                self.errors.append("Se esperaba identificador al final de entrada")

    def parse_lista_sentencias(self):
        # lista_sentencias → { sentencia }
        while True:
            tok = self.current()
            if not tok:
                break
            if tok.type == 4 and tok.value in ('if', 'while', 'do', 'cin', 'cout') or tok.type == 2:
                self.parse_sentencia()
            else:
                break

    def parse_sentencia(self):
        tok = self.current()
        if not tok:
            return
        if tok.type == 4 and tok.value == 'if':
            self.parse_seleccion()
        elif tok.type == 4 and tok.value == 'while':
            self.parse_iteracion()
        elif tok.type == 4 and tok.value == 'do':
            self.parse_repeticion()
        elif tok.type == 4 and tok.value == 'cin':
            self.parse_sent_in()
        elif tok.type == 4 and tok.value == 'cout':
            self.parse_sent_out()
        elif tok.type == 2:
            # check for post-increment/decrement
            nxt = self.peek()
            if nxt and nxt.type == 5 and nxt.value in ('++','--'):
                self.parse_post_increment()
            else:
                self.parse_asignacion()
        else:
            self.errors.append(f"Sentencia inválida '{tok.value}' en línea {tok.line}, col {tok.column}")
            self.advance()

    def parse_post_increment(self):
        """Parse post-increment/decrement statement: id++ ; or id-- ;"""
        # Consume id
        self.match(2)
        # Consume ++ or --
        tok = self.current()
        if tok and tok.type == 5 and tok.value in ('++','--'):
            self.advance()
        else:
            if tok:
                self.errors.append(f"Se esperaba '++' o '--' en línea {tok.line}, col {tok.column}")
        # Expect semicolon
        self.match(7, ';')

    def parse_asignacion(self):
        # id = sent_expresion
        self.match(2)
        self.match(8, '=')
        self.parse_sent_expresion()

    def parse_sent_expresion(self):
        # expresion ; | ;
        tok = self.current()
        if tok and tok.type == 7 and tok.value == ';':
            self.advance()
        else:
            self.parse_expresion()
            self.match(7, ';')

    def parse_seleccion(self):
        # if expresion then lista_sentencias [ else lista_sentencias ] end
        self.match(4, 'if')
        self.parse_expresion()
        self.match(4, 'then')
        self.parse_lista_sentencias()
        tok = self.current()
        if tok and tok.type == 4 and tok.value == 'else':
            self.advance()
            self.parse_lista_sentencias()
        self.match(4, 'end')

    def parse_iteracion(self):
        # while expresion lista_sentencias end
        self.match(4, 'while')
        self.parse_expresion()
        self.parse_lista_sentencias()
        self.match(4, 'end')

    def parse_repeticion(self):
        # do lista_sentencias while expresion
        self.match(4, 'do')
        self.parse_lista_sentencias()
        self.match(4, 'while')
        self.parse_expresion()
        # optional semicolon at end of do-while
        if self.current() and self.current().type == 7 and self.current().value == ';':
            self.advance()

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
        self.match(2)
        self.match(7, ';')

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
        # simple consume until semicolon or end
        while self.current() and not (self.current().type == 7 and self.current().value == ';'):
            self.advance()
        # optional semicolon
        if self.current() and self.current().type == 7 and self.current().value == ';':
            self.advance()

    def parse_expresion(self):
        # parse simple expression
        self.parse_expresion_simple()
        # handle relational operators
        tok = self.current()
        if tok and tok.type == 6 and tok.value in ('<','<=','>','>=','==','!='):
            self.advance()
            self.parse_expresion_simple()
        # handle logical AND/OR operators
        tok = self.current()
        while tok and tok.type == 6 and tok.value in ('&&','||'):
            self.advance()
            self.parse_expresion_simple()
            tok = self.current()

    def parse_expresion_simple(self):
        self.parse_termino()
        while True:
            tok = self.current()
            if tok and tok.type == 5 and tok.value in ('+','-','++','--'):
                self.advance()
                self.parse_termino()
            else:
                break

    def parse_termino(self):
        self.parse_factor()
        while True:
            tok = self.current()
            if tok and tok.type == 5 and tok.value in ('*','/','%'):
                self.advance()
                self.parse_factor()
            else:
                break

    def parse_factor(self):
        self.parse_componente()
        tok = self.current()
        if tok and tok.type == 5 and tok.value == '^':
            self.advance()
            self.parse_componente()

    def parse_componente(self):
        tok = self.current()
        if not tok:
            return
        if tok.type == 7 and tok.value == '(':
            self.advance()
            self.parse_expresion()
            self.match(7, ')')
        elif tok.type in (1,10):  # número
            self.advance()
        elif tok.type == 2:  # id
            self.advance()
        elif tok.type == 4 and tok.value in ('true','false'):  # boolean
            self.advance()
        elif tok.type == 6 and tok.value in ('&&','||','!'):
            self.advance()
            self.parse_componente()
        else:
            # unknown
            self.errors.append(f"Componente inválido '{tok.value}' en línea {tok.line}, col {tok.column}")
            self.advance()
