import re

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class LexicalError:
    def __init__(self, value, line, column, message):
        self.value = value
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        return f"Error: {self.message} '{self.value}' en línea {self.line}, columna {self.column}"

class Lexer:
    def __init__(self):
        # Define token categories
        self.TOKEN_TYPES = {
            'NUMBER': 1,  # Color 1
            'IDENTIFIER': 2,  # Color 2
            'COMMENT': 3,  # Color 3
            'RESERVED': 4,  # Color 4
            'ARITHMETIC_OP': 5,  # Color 5
            'REL_LOG_OP': 6,  # Color 6
            'SYMBOL': 7,  # No specific color mentioned
            'ASSIGNMENT': 8,  # No specific color mentioned
            'ERROR': 9  # For errors
        }
        
        # Define reserved words
        self.RESERVED_WORDS = {
            'if', 'else', 'end', 'do', 'while', 'switch', 'case', 
            'int', 'float', 'main', 'cin', 'cout'
        }
        
        # Define patterns
        self.patterns = [
            # Whitespace (ignored but tracked for line/col counting)
            (r'[ \t]+', None),
            
            # Newlines (tracked for line counting)
            (r'\n', None),
            
            # Comments
            (r'\/\/[^\n]*', self.TOKEN_TYPES['COMMENT']),  # Single line comments
            (r'\/\*[\s\S]*?\*\/', self.TOKEN_TYPES['COMMENT']),  # Multi-line comments
            
            # Numbers
            (r'[+-]?\d+\.\d+', self.TOKEN_TYPES['NUMBER']),  # Real numbers with sign
            (r'[+-]?\d+', self.TOKEN_TYPES['NUMBER']),  # Integer with sign
            
            # Identifiers and reserved words
            (r'[a-zA-Z][a-zA-Z0-9]*', self.recognize_id_or_reserved),
            
            # Arithmetic operators
            (r'\+\+', self.TOKEN_TYPES['ARITHMETIC_OP']),  # increment
            (r'--', self.TOKEN_TYPES['ARITHMETIC_OP']),  # decrement
            (r'[\+\-\*\/\%\^]', self.TOKEN_TYPES['ARITHMETIC_OP']),
            
            # Relational operators
            (r'<=|>=|==|!=|<|>', self.TOKEN_TYPES['REL_LOG_OP']),
            
            # Logical operators
            (r'&&|\|\|', self.TOKEN_TYPES['REL_LOG_OP']),
            
            # Symbols
            (r'[\(\)\{\},;]', self.TOKEN_TYPES['SYMBOL']),
            
            # Assignment
            (r'=', self.TOKEN_TYPES['ASSIGNMENT'])
        ]
        
        # Compile regex patterns
        self.regex_patterns = [(re.compile(pattern), token_type) for pattern, token_type in self.patterns]

    def recognize_id_or_reserved(self, value):
        """Determine if a token is an identifier or reserved word"""
        if value in self.RESERVED_WORDS:
            return self.TOKEN_TYPES['RESERVED']
        return self.TOKEN_TYPES['IDENTIFIER']
        
    def tokenize(self, code):
        """Generate tokens from the input code"""
        tokens = []
        errors = []
        
        lines = code.split('\n')
        line_num = 1
        
        for line in lines:
            col_num = 1
            i = 0
            
            while i < len(line):
                # Try to match a pattern at current position
                matched = False
                
                for pattern, token_type in self.regex_patterns:
                    match = pattern.match(line[i:])
                    
                    if match:
                        value = match.group(0)
                        
                        # Skip whitespace but update column
                        if token_type is None:
                            col_num += len(value)
                            i += len(value)
                            matched = True
                            break
                        
                        # Call function for type identification if needed
                        if callable(token_type):
                            token_type = token_type(value)
                        
                        # Create and add token
                        token = Token(token_type, value, line_num, col_num)
                        tokens.append(token)
                        
                        # Update position
                        col_num += len(value)
                        i += len(value)
                        matched = True
                        break
                
                if not matched:
                    # Handle unrecognized character
                    error = LexicalError(line[i], line_num, col_num, 
                                         "Carácter no reconocido")
                    errors.append(error)
                    i += 1
                    col_num += 1
            
            line_num += 1
        
        return tokens, errors

    def get_color_for_token_type(self, token_type):
        """Return the color for syntax highlighting based on token type"""
        colors = {
            self.TOKEN_TYPES['NUMBER']: '#FFA500',       # Orange
            self.TOKEN_TYPES['IDENTIFIER']: '#A9A9A9',   # Gray
            self.TOKEN_TYPES['COMMENT']: '#006400',      # Dark Green
            self.TOKEN_TYPES['RESERVED']: '#0000FF',     # Blue
            self.TOKEN_TYPES['ARITHMETIC_OP']: '#FF0000', # Red
            self.TOKEN_TYPES['REL_LOG_OP']: '#800080',   # Purple
            self.TOKEN_TYPES['SYMBOL']: '#FFFFFF',       # Black
            self.TOKEN_TYPES['ASSIGNMENT']: '#FFFFFF'    # Black
        }
        return colors.get(token_type, '#000000')  # Default black