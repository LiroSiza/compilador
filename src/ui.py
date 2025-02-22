import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

class IDE:
    def __init__(self, root):
        self.root = root
        self.root.title("IDE para Compilador")
        self.root.geometry("800x600")

        self.filename = None

        # Crear el área de texto para el editor
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True, height=20, width=80)
        self.text_area.pack(padx=10, pady=10)

        # Barra de menús
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Menú de archivo
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_command(label="Guardar como", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)

        # Menú de compilación
        self.compile_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Compilar", menu=self.compile_menu)
        self.compile_menu.add_command(label="Análisis Léxico", command=self.lexical_analysis)
        self.compile_menu.add_command(label="Análisis Sintáctico", command=self.syntax_analysis)
        self.compile_menu.add_command(label="Análisis Semántico", command=self.semantic_analysis)
        self.compile_menu.add_command(label="Código Intermedio", command=self.intermediate_code)
        self.compile_menu.add_command(label="Ejecutar", command=self.execute_code)

        # Area de resultados
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(padx=10, pady=10)

        self.result_text = tk.Text(self.result_frame, height=10, width=80)
        self.result_text.pack()

    def open_file(self):
        """Abre un archivo y carga su contenido en el editor de texto"""
        self.filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if self.filename:
            with open(self.filename, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)

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

    def lexical_analysis(self):
        """Simula el análisis léxico llamando al compilador (se puede usar subprocess para ejecutar otro script)"""
        self.result_text.delete(1.0, tk.END)
        code = self.text_area.get(1.0, tk.END)
        # Aquí realizarías el análisis léxico
        # Por ejemplo, podrías llamar a un script de Python que realice el análisis léxico
        # subprocess.run(["python", "lexical_analyzer.py", code])
        self.result_text.insert(tk.END, "Análisis léxico realizado...\n")

    def syntax_analysis(self):
        """Simula el análisis sintáctico"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Análisis sintáctico realizado...\n")

    def semantic_analysis(self):
        """Simula el análisis semántico"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Análisis semántico realizado...\n")

    def intermediate_code(self):
        """Simula la generación de código intermedio"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Generación de código intermedio...\n")

    def execute_code(self):
        """Simula la ejecución del código"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Ejecutando el código...\n")

if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()
