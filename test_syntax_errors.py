#!/usr/bin/env python3
"""
Script para probar la detección de errores sintácticos en el compilador.
Este script carga el archivo de errores sintácticos y ejecuta el analizador
para verificar que puede detectar correctamente los errores.
"""

import sys
import os
import re

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser

def test_syntax_error_detection():
    """Prueba la capacidad del compilador para detectar errores sintácticos"""
    
    # Ruta al archivo de errores sintácticos
    error_file_path = os.path.join('examples', 'syntax_errors.txt')
    
    # Diccionario para mapear números de error a descripciones
    error_descriptions = {}
    
    # Leer el archivo y extraer los comentarios de error
    try:
        with open(error_file_path, 'r') as f:
            content = f.read()
            
            # Buscar patrones de comentarios de error
            error_pattern = r'// ERROR (\d+): (.*?)$'
            matches = re.finditer(error_pattern, content, re.MULTILINE)
            
            for match in matches:
                error_num = int(match.group(1))
                description = match.group(2)
                error_descriptions[error_num] = description
    except FileNotFoundError:
        print(f"El archivo {error_file_path} no fue encontrado.")
        return
    
    print("=" * 80)
    print("PRUEBA DE DETECCIÓN DE ERRORES SINTÁCTICOS")
    print("=" * 80)
    print(f"Archivo de prueba: {error_file_path}")
    print(f"Total de errores a detectar: {len(error_descriptions)}")
    print("-" * 80)
    
    # Dividir el archivo en secciones de código (cada una con un error diferente)
    code_sections = []
    current_section = []
    error_num = 0
    
    # Leer el archivo de nuevo para procesar líneas
    with open(error_file_path, 'r') as f:
        for line in f:
            # Comprobar si es una nueva sección de error
            error_match = re.search(r'// ERROR (\d+):', line)
            if error_match and current_section:
                # Guardar la sección anterior
                code_sections.append((error_num, '\n'.join(current_section)))
                current_section = []
            
            # Actualizar el número de error si es necesario
            if error_match:
                error_num = int(error_match.group(1))
            
            # Añadir la línea a la sección actual si no es un comentario principal de error
            if not line.strip().startswith('// ERROR'):
                current_section.append(line.rstrip())
    
    # Añadir la última sección
    if current_section:
        code_sections.append((error_num, '\n'.join(current_section)))
    
    # Procesar cada sección de código
    successful_detections = 0
    
    for error_num, code in code_sections:
        if error_num == 0 or not code.strip():
            continue  # Saltar secciones vacías o sin número de error
            
        print(f"\nPrueba de ERROR #{error_num}: {error_descriptions.get(error_num, 'Sin descripción')}")
        print("-" * 40)
        
        # Mostrar un extracto del código
        code_lines = code.split('\n')
        print("Código:")
        for i, line in enumerate(code_lines):
            if i < 5:  # Mostrar máximo 5 líneas
                print(f"  {line}")
            elif i == 5:
                print("  ...")
        
        # Ejecutar el análisis léxico
        lexer = Lexer()
        tokens, lex_errors = lexer.tokenize(code)
        
        if lex_errors:
            print("\nErrores léxicos detectados:")
            for error in lex_errors[:3]:  # Mostrar hasta 3 errores
                print(f"  {error}")
            if len(lex_errors) > 3:
                print(f"  ... y {len(lex_errors) - 3} más")
        
        # Ejecutar el análisis sintáctico
        parser = Parser(tokens)
        ast, parse_errors = parser.parse()
        
        if parse_errors:
            print("\nErrores sintácticos detectados:")
            for i, error in enumerate(parse_errors[:3]):  # Mostrar hasta 3 errores
                print(f"  {error}")
            if len(parse_errors) > 3:
                print(f"  ... y {len(parse_errors) - 3} más")
            
            print("\n✓ Error detectado correctamente")
            successful_detections += 1
        else:
            print("\n❌ ERROR: El compilador no detectó ningún error sintáctico")
    
    # Mostrar resultados finales
    print("\n" + "=" * 80)
    print(f"RESUMEN: Detectados {successful_detections} de {len(code_sections)} errores")
    print(f"Tasa de éxito: {successful_detections / len(code_sections) * 100:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    test_syntax_error_detection()
