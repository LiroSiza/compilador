from src.ui import IDE
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)  # Instanciamos la clase IDE y la asociamos a la ventana principal
    root.mainloop()   # Iniciamos el bucle de eventos de Tkinter
