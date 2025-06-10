import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import Lexer
from lexer import Lexer
from parser import Parser

class IDE:
    def __init__(self, root):
        self.last_analysis_text = ""
        self._syntax_highlight_after = None
        # Define color scheme
        self.colors = {
            'bg_main': '#1a1a2e',  # Dark navy blue
            'bg_secondary': '#16213e',  # Slightly lighter navy blue
            'fg_main': '#ffffff',  # White text
            'fg_secondary': '#e1e1e1',  # Slightly dimmed white
            'accent': '#0f3460',  # Accent color for buttons
            'error_bg': '#2a1f2d',  # Dark red background for errors
            'result_bg': '#1f2a2d'  # Dark blue-green background for results
        }

        # Add font configuration
        self.fonts = {
            'editor': ('Consolas', 12),  # Modern monospace font for code
            'line_numbers': ('Consolas', 12),
            'buttons': ('Segoe UI', 10),
            'labels': ('Segoe UI', 10),
            'results': ('Consolas', 11)
        }

        self.root = root
        self.root.title("IDE para Compilador")
        self.root.geometry("1000x800")
        self.root.configure(bg=self.colors['bg_main'])

        # Frame principal
        self.main_frame = tk.PanedWindow(self.root, orient=tk.VERTICAL, bg=self.colors['bg_main'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)


        # Toolbar frame
        self.toolbar_frame = tk.Frame(self.main_frame, bg=self.colors['bg_main'])
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # Load and resize toolbar icons
        try:
            def load_and_resize_icon(path, size=(16, 16)):
                img = tk.PhotoImage(file=path)
                # Create a temporary canvas to resize the image
                canvas = tk.Canvas(width=size[0], height=size[1])
                canvas.image = img  # Keep a reference
                return img.subsample(max(1, img.width() // size[0]), max(1, img.height() // size[1]))

            self.new_icon = load_and_resize_icon("assets/new-document.png")
            self.open_icon = load_and_resize_icon("assets/open-file.png")
            self.save_icon = load_and_resize_icon("assets/save.png")
        except tk.TclError:
            print("Warning: Could not load toolbar icons")
            self.new_icon = None
            self.open_icon = None
            self.save_icon = None

        # Create toolbar buttons
        toolbar_button_style = {
            'bg': self.colors['bg_main'],
            'activebackground': self.colors['accent'],
            'bd': 0,
            'padx': 5,
            'pady': 5,
            'cursor': 'hand2',
            'width': 24,  # Fixed width for buttons
            'height': 24  # Fixed height for buttons
        }

        self.btn_new = tk.Button(self.toolbar_frame, 
                                image=self.new_icon if self.new_icon else None,
                                text="" if self.new_icon else "New",
                                command=self.new_file,
                                **toolbar_button_style)
        self.btn_new.pack(side=tk.LEFT, padx=2)

        self.btn_open = tk.Button(self.toolbar_frame, 
                                 image=self.open_icon if self.open_icon else None,
                                 text="" if self.open_icon else "Open",
                                 command=self.open_file,
                                 **toolbar_button_style)
        self.btn_open.pack(side=tk.LEFT, padx=2)

        self.btn_save = tk.Button(self.toolbar_frame, 
                                 image=self.save_icon if self.save_icon else None,
                                 text="" if self.save_icon else "Save",
                                 command=self.save_file,
                                 **toolbar_button_style)
        self.btn_save.pack(side=tk.LEFT, padx=2)

        # Frame superior para el editor
        self.editor_frame = tk.Frame(self.main_frame, bg=self.colors['bg_main'])
        self.main_frame.add(self.editor_frame, stretch="always")


        # Frame for editor and line numbers
        self.editor_with_lines_frame = tk.Frame(self.editor_frame, bg=self.colors['bg_main'])
        self.editor_with_lines_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Line numbers text widget - adjust width and add proper styling
        self.line_numbers = tk.Text(self.editor_with_lines_frame, width=4)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.config(
            bg=self.colors['bg_main'],
            fg=self.colors['fg_secondary'],
            font=self.fonts['line_numbers'],
            padx=5,
            pady=5,
            borderwidth=0,
            highlightthickness=0,
            spacing1=2,  # Match main editor spacing
            spacing2=2,
            spacing3=2
        )

        # Main text area - ensure consistent spacing
        self.text_area = tk.Text(self.editor_with_lines_frame, wrap=tk.NONE, undo=True)  # Changed wrap to NONE
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_main'],
            insertbackground=self.colors['fg_main'],
            selectbackground='#344055',
            selectforeground=self.colors['fg_main'],
            font=self.fonts['editor'],
            padx=5,
            pady=5,
            spacing1=2,
            spacing2=2,
            spacing3=2
        )

        # Main editor scrollbar setup - MOVE THIS HERE
        self.editor_scroll = tk.Scrollbar(self.editor_with_lines_frame)
        self.editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure editor scrollbar
        self.text_area.config(yscrollcommand=self.editor_scroll.set)
        self.editor_scroll.config(command=self.on_scroll)  # Use on_scroll instead of yview

        # Bind events for updating line numbers and cursor position
        self.text_area.bind('<Key>', self.update_line_numbers)
        self.text_area.bind('<KeyRelease>', lambda e: (self.update_line_numbers(), self.update_cursor_position()))
        self.text_area.bind('<Button-1>', lambda e: (self.update_line_numbers(), self.update_cursor_position()))
        self.text_area.bind('<ButtonRelease-1>', self.update_cursor_position)
        self.text_area.bind('<MouseWheel>', self.update_line_numbers)
        self.text_area.bind('<<Change>>', self.update_line_numbers)
        self.text_area.bind('<Configure>', self.update_line_numbers)
        
        # Add these new bindings
        self.text_area.bind('<Return>', self.update_line_numbers)
        self.text_area.bind('<BackSpace>', self.update_line_numbers)
        self.text_area.bind('<Delete>', self.update_line_numbers)

        # Initial line numbers
        self.update_line_numbers()

        # Cursor position label - move to bottom and ensure visibility
        self.cursor_label = tk.Label(self.main_frame, text="Línea: 1, Columna: 1")
        self.cursor_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=2)

        # Configure line numbers
        self.line_numbers.tag_configure('line', justify='right')
        self.line_numbers.config(bg=self.colors['bg_main'], fg=self.colors['fg_secondary'])
        self.line_numbers.config(state='disabled')

        # Frame inferior para resultados y errores
        self.output_frame = tk.Frame(self.main_frame, bg=self.colors['bg_main'])
        self.main_frame.add(self.output_frame, stretch="always")


        # Crear el área de texto para el editor (70% del alto)
        # self.text_area = tk.Text(self.editor_frame, wrap=tk.WORD, undo=True)
        # self.text_area.pack(fill=tk.BOTH, expand=True)

        # Frame para resultados y errores (30% del alto)
        self.results_errors_frame = tk.Frame(self.output_frame, bg=self.colors['bg_main'])
        self.results_errors_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para resultados (izquierda)
        self.results_frame = tk.LabelFrame(self.results_errors_frame, text="Resultados", bg=self.colors['bg_main'], fg=self.colors['fg_main'])
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Frame para los botones de resultados
        self.results_buttons_frame = tk.Frame(self.results_frame, bg=self.colors['bg_main'])
        self.results_buttons_frame.pack(fill=tk.X, padx=5, pady=2)        # Botones para cambiar vista de resultados
        self.btn_lexico = tk.Button(self.results_buttons_frame, text="Léxico", 
                                  command=self.show_lexical_results)
        self.btn_lexico.pack(side=tk.LEFT, padx=2)
        
        self.btn_sintactico = tk.Button(self.results_buttons_frame, text="Sintáctico", 
                                      command=self.syntax_analysis)
        self.btn_sintactico.pack(side=tk.LEFT, padx=2)
        
        self.btn_semantico = tk.Button(self.results_buttons_frame, text="Semántico", 
                                     command=lambda: self.show_result("semantico"))
        self.btn_semantico.pack(side=tk.LEFT, padx=2)
        
        self.btn_tabla = tk.Button(self.results_buttons_frame, text="Tabla Hash", 
                                 command=lambda: self.show_result("tabla"))
        self.btn_tabla.pack(side=tk.LEFT, padx=2)
        
        self.btn_intermedio = tk.Button(self.results_buttons_frame, text="Intermedio", 
                                      command=lambda: self.show_result("intermedio"))
        self.btn_intermedio.pack(side=tk.LEFT, padx=2)        # Área de texto para resultados (después de los botones)
        self.result_text = tk.Text(self.results_frame)  # Increased height from 10 to 15

        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para el AST (inicialmente oculto)
        self.ast_tree = ttk.Treeview(self.results_frame)
        self.ast_tree['columns'] = ('type', 'value', 'line', 'column')
        self.ast_tree.heading('#0', text='Nodo')
        self.ast_tree.heading('type', text='Tipo')
        self.ast_tree.heading('value', text='Valor')
        self.ast_tree.heading('line', text='Línea')
        self.ast_tree.heading('column', text='Columna')
        
        # Configurar anchos de columna
        self.ast_tree.column('#0', width=200, minwidth=150)
        self.ast_tree.column('type', width=150, minwidth=100)
        self.ast_tree.column('value', width=100, minwidth=80)
        self.ast_tree.column('line', width=60, minwidth=50)
        self.ast_tree.column('column', width=60, minwidth=50)
        
        # Inicialmente oculto
        self.ast_tree.pack_forget()

        # Scrollbar para el AST
        self.ast_scroll = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.ast_tree.yview)
        self.ast_tree.configure(yscrollcommand=self.ast_scroll.set)
        self.ast_scroll.pack_forget()

        # Frame para errores (derecha)
        self.errors_frame = tk.LabelFrame(self.results_errors_frame, text="Errores", bg=self.colors['bg_main'], fg=self.colors['fg_main'])
        self.errors_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para los botones de errores
        self.errors_buttons_frame = tk.Frame(self.errors_frame, bg=self.colors['bg_main'])
        self.errors_buttons_frame.pack(fill=tk.X, padx=5, pady=2)

        # Botones para cambiar vista de errores
        self.btn_err_lexico = tk.Button(self.errors_buttons_frame, text="Léxico", 
                                      command=lambda: self.show_error("lexico"))
        self.btn_err_lexico.pack(side=tk.LEFT, padx=2)
        
        self.btn_err_sintactico = tk.Button(self.errors_buttons_frame, text="Sintáctico", 
                                          command=lambda: self.show_error("sintactico"))
        self.btn_err_sintactico.pack(side=tk.LEFT, padx=2)
        
        self.btn_err_semantico = tk.Button(self.errors_buttons_frame, text="Semántico", 
                                         command=lambda: self.show_error("semantico"))
        self.btn_err_semantico.pack(side=tk.LEFT, padx=2)
        
        self.btn_err_resultados = tk.Button(self.errors_buttons_frame, text="Resultados", 
                                          command=lambda: self.show_error("resultados"))
        self.btn_err_resultados.pack(side=tk.LEFT, padx=2)

        # Área de texto para errores (después de los botones)
        self.error_text = tk.Text(self.errors_frame)  # Increased height from 10 to 15        self.error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results scrollbar setup
        self.result_scroll = tk.Scrollbar(self.results_frame)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure results scrollbar
        self.result_text.config(yscrollcommand=self.result_scroll.set)
        self.result_scroll.config(command=self.result_text.yview)

        # Error scrollbar setup
        self.error_scroll = tk.Scrollbar(self.errors_frame)
        self.error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.error_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure error scrollbar
        self.error_text.config(yscrollcommand=self.error_scroll.set)
        self.error_scroll.config(command=self.error_text.yview)

        # Configurar colores para diferenciar las áreas
        self.text_area.config(
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_main'],
            insertbackground=self.colors['fg_main'],  # Cursor color
            selectbackground='#344055',  # Selection color
            selectforeground=self.colors['fg_main'],
            font=self.fonts['editor'],
            pady=5,
            padx=5,
            spacing1=2,  # Space between lines
            spacing2=2,  # Space between paragraphs
            spacing3=2   # Space when word-wrapped
        )

        self.result_text.config(
            bg=self.colors['result_bg'],
            fg=self.colors['fg_main']
        )

        self.error_text.config(
            bg=self.colors['error_bg'],
            fg=self.colors['fg_main']
        )

        # Update line numbers configuration
        self.line_numbers.config(
            bg=self.colors['bg_main'],
            fg=self.colors['fg_secondary'],
            font=self.fonts['line_numbers'],
            pady=5,
            padx=5,
            borderwidth=0,
            highlightthickness=0
        )

        # Update result and error text areas
        for text_widget in [self.result_text, self.error_text]:
            text_widget.config(
                font=self.fonts['results'],
                pady=5,
                padx=5,
                spacing1=2,
                spacing2=2,
                spacing3=2,
                borderwidth=0,
                highlightthickness=1,
                highlightbackground=self.colors['accent']
            )

        # Make error and result text readonly
        self.result_text.config(state='disabled')
        self.error_text.config(state='disabled')

        # Añadir frame para botones
        self.button_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.button_frame.pack(padx=10, pady=5)

        # Barra de menús
        self.menu_bar = tk.Menu(self.root, bg=self.colors['bg_main'], fg=self.colors['fg_main'])
        self.root.config(menu=self.menu_bar)

        # Menú de archivo (dropdown)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_command(label="Guardar como", command=self.save_as_file)
        self.file_menu.add_command(label="Cerrar", command=self.close_file)  # Add close option
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)

        # Menú de compilación (dropdown)
        self.compile_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Compilar", menu=self.compile_menu)
        self.compile_menu.add_command(label="Análisis Léxico", command=self.lexical_analysis)
        self.compile_menu.add_command(label="Análisis Sintáctico", command=self.syntax_analysis)
        self.compile_menu.add_command(label="Análisis Semántico", command=self.semantic_analysis)
        self.compile_menu.add_command(label="Código Intermedio", command=self.intermediate_code)
        self.compile_menu.add_command(label="Ejecutar", command=self.execute_code)

        # Botones directos en la barra de menú
        self.menu_bar.add_command(label="Léxico", command=self.lexical_analysis)
        self.menu_bar.add_command(label="Sintáctico", command=self.syntax_analysis)
        self.menu_bar.add_command(label="Semántico", command=self.semantic_analysis)
        self.menu_bar.add_command(label="Intermedio", command=self.intermediate_code)
        self.menu_bar.add_command(label="Ejecutar", command=self.execute_code)

        # Configure button style
        button_style = {
            'bg': self.colors['accent'],
            'fg': self.colors['fg_main'],
            'activebackground': self.colors['bg_secondary'],
            'activeforeground': self.colors['fg_main'],
            'font': self.fonts['buttons'],
            'relief': 'flat',
            'borderwidth': 0,
            'highlightthickness': 0,
            'pady': 3,
            'padx': 10,
            'cursor': 'hand2'
        }

        # Apply style to all buttons
        all_buttons = [
            self.btn_lexico, self.btn_sintactico, self.btn_semantico, 
            self.btn_tabla, self.btn_intermedio, self.btn_err_lexico, 
            self.btn_err_sintactico, self.btn_err_semantico, 
            self.btn_err_resultados  # Removed btn_err_intermedio from this list
        ]
        
        for btn in all_buttons:
            btn.configure(**button_style)

        # Configure menu item colors
        menu_config = {
            'activebackground': self.colors['accent'],
            'activeforeground': self.colors['fg_main'],
            'background': self.colors['bg_secondary'],
            'foreground': self.colors['fg_main']
        }
        
        self.file_menu.configure(**menu_config)
        self.compile_menu.configure(**menu_config)

        # Update menu configuration
        menu_config.update({
            'font': self.fonts['buttons']
        })

        # Update scrollbar colors
        scrollbar_style = {
            'bg': self.colors['bg_secondary'],
            'troughcolor': self.colors['bg_main'],
            'activebackground': self.colors['accent']
        }
        
        self.editor_scroll.configure(**scrollbar_style)
        self.result_scroll.configure(**scrollbar_style)
        self.error_scroll.configure(**scrollbar_style)

        # Configure cursor label
        self.cursor_label.configure(
            bg=self.colors['bg_main'],
            fg=self.colors['fg_secondary'],
            font=self.fonts['labels'],
            pady=5
        )

        # Add highlight colors for text selection
        self.text_area.tag_configure("sel", 
            background="#344055", 
            foreground=self.colors['fg_main']
        )

    def on_scroll(self, *args):
        """Handle scrolling of text area and line numbers"""
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()

    def open_file(self):
        """Abre un archivo y carga su contenido en el editor de texto"""
        self.filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if self.filename:
            with open(self.filename, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.update_line_numbers()  # Add this line
                self.lexical_analysis()

    def save_file(self):
        """Guarda el archivo actual"""
        if self.filename:
            with open(self.filename, "w") as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Guarda el archivo con un nombre nuevo"""
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if self.filename:
            self.save_file()

    def update_result(self, text):
        """Update the result text area"""
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state='disabled')

    def update_error(self, text):
        """Update the error text area"""
        self.error_text.config(state='normal')
        self.error_text.delete(1.0, tk.END)
        self.error_text.insert(tk.END, text)
        self.error_text.config(state='disabled')

    def lexical_analysis(self):
        """Performs lexical analysis on the code"""
        try:
            code = self.text_area.get(1.0, tk.END)
            lexer = Lexer()
            tokens, errors = lexer.tokenize(code, save_to_file=True, output_filename="tokens.txt")
            
            # Store the analyzed text to avoid unnecessary repeated analysis
            self.last_analysis_text = code
            
            # Update result with tokens
            result_text = "Análisis léxico realizado...\n\n"
            for token in tokens:
                result_text += str(token) + "\n"
            self.update_result(result_text)
            
            # Update error with errors
            if errors:
                error_text = "Se encontraron errores léxicos:\n\n"
                for error in errors:
                    error_text += str(error) + "\n"
                self.update_error(error_text)
            else:
                self.update_error("No se encontraron errores léxicos\n")
            
            # Store tokens for syntax analysis
            self.last_tokens = tokens
            # Apply syntax highlighting
            self.apply_syntax_highlighting(tokens)
        except Exception as e:
            import traceback
            error_message = f"Error al realizar el análisis léxico:\n{str(e)}\n\n"
            error_message += traceback.format_exc()
            self.update_error(error_message)
            print(error_message)

    # Add a new method to apply syntax highlighting
    def apply_syntax_highlighting(self, tokens):
        """Apply syntax highlighting to the text based on token types"""
        # First, remove any existing tags
        for tag in self.text_area.tag_names():
            if tag != "sel":  # Don't remove selection tag
                self.text_area.tag_remove(tag, "1.0", tk.END)
        
        # Apply highlighting for each token
        lexer = Lexer()
        for token in tokens:
            # Calculate positions
            start_pos = f"{token.line}.{token.column-1}"
            end_pos = f"{token.line}.{token.column-1 + len(token.value)}"
            
            # Create a tag for this token type if it doesn't exist
            tag_name = f"token_{token.type}"
            if tag_name not in self.text_area.tag_names():
                color = lexer.get_color_for_token_type(token.type)
                self.text_area.tag_configure(tag_name, foreground=color)
              # Apply the tag
            self.text_area.tag_add(tag_name, start_pos, end_pos)

    def syntax_analysis(self):
        """Realiza el análisis sintáctico usando el Parser y muestra el AST"""
        try:
            # Ensure tokens are available
            if not hasattr(self, 'last_tokens'):
                self.lexical_analysis()
            
            # Parse tokens and get AST
            parser = Parser(self.last_tokens)
            ast_root, errors = parser.parse()
            
            # Hide result text and show AST tree
            self.result_text.pack_forget()
            
            # Clear previous AST content
            for item in self.ast_tree.get_children():
                self.ast_tree.delete(item)
            
            # Show AST tree and scrollbar
            self.ast_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side=tk.LEFT)
            self.ast_scroll.pack(fill=tk.Y, side=tk.RIGHT)
              # Populate AST tree
            if ast_root:
                self._populate_ast_tree('', ast_root)
                # Expand all nodes to show the complete tree structure
                self._expand_all_nodes()
            
            # Update errors
            if errors:
                error_text = "Se encontraron errores sintácticos:\n\n" + "\n".join(errors)
                self.update_error(error_text)
            else:
                self.update_error("No se encontraron errores sintácticos\n")
                
        except Exception as e:
            import traceback
            error_message = f"Error en análisis sintáctico:\n{str(e)}\n\n{traceback.format_exc()}"
            self.update_error(error_message)
            # Show result text again if there's an error            self.ast_tree.pack_forget()
            self.ast_scroll.pack_forget()
            self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.update_result("Error en el análisis sintáctico")

    def _get_operation_type(self, operator):
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

    def _populate_ast_tree(self, parent, node):
        """Populate the AST tree recursively"""
        if not node:
            return
            
        # Create display text for the node
        node_text = node.type
        
        # Determine the type to show in the Type column
        display_type = node.type
        
        # For binary operations, show the specific operation type
        if node.type == "operacion_binaria" and hasattr(node, 'value') and node.value is not None:
            operation_type = self._get_operation_type(node.value)
            display_type = operation_type
            node_text = f"{node.type} ({operation_type})"
        elif node.type == "operacion_unaria" and hasattr(node, 'value') and node.value is not None:
            operation_type = self._get_operation_type(node.value)
            display_type = operation_type
            node_text = f"{node.type} ({operation_type})"
        elif hasattr(node, 'value') and node.value is not None:
            node_text += f" ({node.value})"
        
        # Insert the node into the tree
        item = self.ast_tree.insert(parent, 'end', text=node_text, values=(
            display_type,
            str(node.value) if hasattr(node, 'value') and node.value is not None else '',
            str(node.line) if hasattr(node, 'line') and node.line is not None else '',
            str(node.column) if hasattr(node, 'column') and node.column is not None else ''
        ))
          # Add children recursively
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._populate_ast_tree(item, child)
        
        # Expand this node to show its children by default
        self.ast_tree.item(item, open=True)

    def _expand_all_nodes(self):
        """Expand all nodes in the tree to show the complete structure"""
        def expand_node(item):
            self.ast_tree.item(item, open=True)
            children = self.ast_tree.get_children(item)
            for child in children:
                expand_node(child)
        
        # Expand all root nodes
        root_items = self.ast_tree.get_children()
        for item in root_items:
            expand_node(item)

    def show_lexical_results(self):
        """Switch back to showing lexical analysis results"""
        self.ast_tree.pack_forget()
        self.ast_scroll.pack_forget()
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Re-run lexical analysis to show tokens
        self.lexical_analysis()

    def semantic_analysis(self):
        """Simula el análisis semántico"""
        self.update_result("Análisis semántico realizado...\n")
        self.update_error("No se encontraron errores semánticos\n")

    def intermediate_code(self):
        """Simula la generación de código intermedio"""
        self.update_result("Generación de código intermedio...\n")
        self.update_error("No se encontraron errores en la generación de código intermedio\n")

    def execute_code(self):
        """Simula la ejecución del código"""
        self.update_result("Ejecutando el código...\n")
        self.update_error("No se encontraron errores en la ejecución del código\n")
    
    def show_result(self, result_type):
        """Muestra el resultado correspondiente al botón presionado"""
        results = {
            "lexico": "Resultados del análisis léxico:\n",
            "sintactico": "Resultados del análisis sintáctico:\n",
            "semantico": "Resultados del análisis semántico:\n",
            "tabla": "Tabla de símbolos:\n",
            "intermedio": "Código intermedio generado:\n"
        }
        
        self.update_result(results.get(result_type, "Seleccione un tipo de resultado"))

    def show_error(self, error_type):
        """Muestra los errores correspondientes al botón presionado"""
        errors = {
            "lexico": "Errores del análisis léxico:\n",
            "sintactico": "Errores del análisis sintáctico:\n",
            "semantico": "Errores del análisis semántico:\n",
            "resultados": "Errores en los resultados:\n"
        }
        
        self.update_error(errors.get(error_type, "Seleccione un tipo de error"))

    def update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        # Get text content and count lines
        text_content = self.text_area.get('1.0', tk.END)
        
        # Handle empty text area
        if len(text_content) <= 1:  # Just contains '\n'
            self.line_numbers.insert('1.0', '  1')
            self.line_numbers.config(state='disabled')
            return
        
        # Count lines
        num_lines = text_content.count('\n')
        if not text_content.endswith('\n'):  # Fix: changed endsWith to endswith
            num_lines += 1
        
        # Create line numbers with padding
        line_numbers_text = '\n'.join(str(i).rjust(3) for i in range(1, num_lines + 1))
        
        # Insert line numbers
        self.line_numbers.insert('1.0', line_numbers_text)
        
        # Sync scrolling
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        self.line_numbers.config(state='disabled')
        if hasattr(self, 'last_analysis_text') and self.last_analysis_text != self.text_area.get(1.0, tk.END):
            # Only re-run analysis if significant time has passed (to avoid performance issues)
            if hasattr(self, '_syntax_highlight_after') and self._syntax_highlight_after:
                self.root.after_cancel(self._syntax_highlight_after)
            # Reduce from 1000ms to 300ms for better responsiveness
            self._syntax_highlight_after = self.root.after(300, self.lexical_analysis)
    def update_cursor_position(self, event=None):
        """Update cursor position indicator"""
        try:
            position = self.text_area.index(tk.INSERT)
            line, col = position.split('.')
            # Adjust column to be 1-based instead of 0-based
            col = str(int(col) + 1)
            self.cursor_label.config(text=f"Línea: {line}, Columna: {col}")
        except Exception as e:
            self.cursor_label.config(text="Línea: 1, Columna: 1")
    
    def close_file(self):
        """Cierra el archivo actual y limpia el editor"""
        if self.has_unsaved_changes():
            response = messagebox.askyesnocancel(
                "Guardar cambios",
                "¿Desea guardar los cambios antes de cerrar?")
            
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_file()
                if not self.filename:  # If save was cancelled
                    return
        
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.update_line_numbers()

    def has_unsaved_changes(self):
        """Verifica si hay cambios sin guardar"""
        if not hasattr(self, 'filename'):
            return self.text_area.get(1.0, tk.END) != '\n'
        
        try:
            with open(self.filename, 'r') as file:
                original_content = file.read()
                current_content = self.text_area.get(1.0, tk.END)
                return original_content != current_content
        except:
            return True
    def new_file(self):
        """Creates a new empty file"""
        if hasattr(self, 'filename') and self.has_unsaved_changes():
            response = messagebox.askyesnocancel(
                "Guardar cambios",
                "¿Desea guardar los cambios antes de crear un nuevo archivo?")
            
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_file()
                if not self.filename:  # If save was cancelled
                    return
        
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.update_line_numbers()
        self.update_cursor_position()

if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()
