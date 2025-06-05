import re

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        # Get the token type name instead of just the number
        token_names = {
            1: "ENTERO",
            10: "DECIMAL",
            2: "IDENTIFICADOR",
            3: "COMENTARIO",
            4: "RESERVADO",
            5: "OP_ARITM",
            6: "OP_REL",
            7: "SIMBOLO",
            8: "ASIGNACION",
            9: "ERROR"
        }
        type_name = token_names.get(self.type, str(self.type))
        return f"Token({type_name}, '{self.value}', line={self.line}, col={self.column})"
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
            'INTEGER': 1,      # Integer numbers
            'DECIMAL': 10,     # Decimal (floating point) numbers
            'IDENTIFIER': 2,   # Identifiers
            'COMMENT': 3,      # Comments
            'RESERVED': 4,     # Reserved words
            'ARITHMETIC_OP': 5, # Arithmetic operators
            'REL_LOG_OP': 6,   # Relational/logical operators
            'SYMBOL': 7,       # Symbols
            'ASSIGNMENT': 8,   # Assignment
            'ERROR': 9         # Errors
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
            (r'//[^\n]*', self.TOKEN_TYPES['COMMENT']),  # Single line comments 
            (r'/\*(.|\n)*?\*/', self.TOKEN_TYPES['COMMENT']),  # Multi-line comments

            # Arithmetic operators
            (r'\+\+', self.TOKEN_TYPES['ARITHMETIC_OP']),  # increment
            (r'--', self.TOKEN_TYPES['ARITHMETIC_OP']),  # decrement
            (r'[\+\-\*\/\%\^]', self.TOKEN_TYPES['ARITHMETIC_OP']),
            
            # Numbers
            (r'\d+\.\d+', self.TOKEN_TYPES['DECIMAL']),  # Valid decimal (digits on both sides)
            (r'\d+\.(?![0-9])', self.TOKEN_TYPES['ERROR']),  # Invalid decimal (no digits after dot)
            (r'\d+', self.TOKEN_TYPES['INTEGER']),       # Integer
            
            # Identifiers and reserved words
            (r'[a-zA-Z][a-zA-Z0-9]*', self.recognize_id_or_reserved),
            
            
            
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

    def save_tokens_to_file(self, tokens, filename="tokens.txt"):
        """Write the list of tokens to a text file."""
        with open(filename, "w", encoding="utf-8") as f:
            for t in tokens:
                f.write(f"{t.type} {t.value} {t.line} {t.column}\n")


    def recognize_id_or_reserved(self, value):
        """Determine if a token is an identifier or reserved word"""
        if value in self.RESERVED_WORDS:
            return self.TOKEN_TYPES['RESERVED']
        return self.TOKEN_TYPES['IDENTIFIER']
        
    def tokenize(self, code, save_to_file=False, output_filename="tokens.txt"):
        """Generate tokens from the input code"""
        tokens = []
        errors = []
        
        # First, extract all multiline comments
        multiline_pattern = re.compile(r'/\*[\s\S]*?\*/', re.DOTALL)
        
        # Find all multiline comment positions
        comment_matches = list(multiline_pattern.finditer(code))
        
        # Process the code with comments handled separately
        pos = 0
        line_num = 1
        col_num = 1
        
        for match in comment_matches:
            # Process text before this comment
            pre_comment = code[pos:match.start()]
            pre_tokens, pre_errors, line_num, col_num = self._process_text(pre_comment, line_num, col_num)
            tokens.extend(pre_tokens)
            errors.extend(pre_errors)
            
            # Create token for the comment
            comment_text = match.group(0)
            comment_lines = comment_text.count('\n')
            
            # Find line and column of comment start
            comment_line = line_num
            comment_col = col_num
            
            # Add the comment token
            token = Token(self.TOKEN_TYPES['COMMENT'], comment_text, comment_line, comment_col)
            tokens.append(token)
            
            # Update position
            pos = match.end()
            line_num += comment_lines
            if comment_lines > 0:
                col_num = len(comment_text.split('\n')[-1]) + 1
            else:
                col_num += len(comment_text)
        
        # Process remaining text
        remaining = code[pos:]
        rem_tokens, rem_errors, _, _ = self._process_text(remaining, line_num, col_num)
        tokens.extend(rem_tokens)
        errors.extend(rem_errors)

        if save_to_file:
            self.save_tokens_to_file(tokens, output_filename)
        
        return tokens, errors

    def _process_text(self, text, start_line, start_col):
        """Helper method to process text without multiline comments"""
        tokens = []
        errors = []
        
        lines = text.split('\n')
        line_num = start_line
        col_num = start_col
        
        for i, line in enumerate(lines):
            # Reset column for new lines (except the first one)
            if i > 0:
                col_num = 1
            
            j = 0
            while j < len(line):
                # Try to match a pattern at current position
                matched = False
                
                for pattern, token_type in self.regex_patterns:
                    match = pattern.match(line[j:])
                    
                    if match:
                        value = match.group(0)
                        
                        # Skip whitespace but update column
                        if token_type is None:
                            col_num += len(value)
                            j += len(value)
                            matched = True
                            break
                        
                        # Skip multiline comment patterns - we already handled them
                        if token_type == self.TOKEN_TYPES['COMMENT'] and '/*' in value:
                            matched = True
                            j += len(value)
                            col_num += len(value)
                            break
                        
                        # Call function for type identification if needed
                        if callable(token_type):
                            token_type = token_type(value)
                        
                        # Check if this is an error token (invalid decimal)
                        if token_type == self.TOKEN_TYPES['ERROR']:
                            # Create an error instead of a token
                            error_msg = "Número decimal inválido" if '.' in value else "Error léxico"
                            error = LexicalError(value, line_num, col_num, error_msg)
                            errors.append(error)
                        else:
                            # Create and add regular token
                            token = Token(token_type, value, line_num, col_num)
                            tokens.append(token)
                        
                        # Update position
                        col_num += len(value)
                        j += len(value)
                        matched = True
                        break
                
                if not matched:
                    # Handle unrecognized character
                    error = LexicalError(line[j], line_num, col_num, "Carácter no reconocido")
                    errors.append(error)
                    j += 1
                    col_num += 1
            
            line_num += 1
        
        return tokens, errors, line_num, col_num

    def get_color_for_token_type(self, token_type):
        """Return the color for syntax highlighting based on token type"""
        colors = {
            self.TOKEN_TYPES['INTEGER']: '#FFA500',     # Orange for integers
            self.TOKEN_TYPES['DECIMAL']: '#FF8C00',     # Dark orange for decimals
            self.TOKEN_TYPES['IDENTIFIER']: '#A9A9A9',  # Gray
            self.TOKEN_TYPES['COMMENT']: '#006400',     # Dark Green
            self.TOKEN_TYPES['RESERVED']: '#0000FF',    # Blue
            self.TOKEN_TYPES['ARITHMETIC_OP']: '#FF0000', # Red
            self.TOKEN_TYPES['REL_LOG_OP']: '#800080',  # Purple
            self.TOKEN_TYPES['SYMBOL']: '#FFFFFF',      # White
            self.TOKEN_TYPES['ASSIGNMENT']: '#FFFFFF'   # White
        }
        return colors.get(token_type, '#000000')   # Default black