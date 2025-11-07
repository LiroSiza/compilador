# compilador
Compilador

### Setting up the Development Environment

1. Clone the repository (if using Git):
   ```bash
   git clone <repository-url>
   cd compilador
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt

   ```

5.- Run:

    set TCL_LIBRARY=C:\Users\Rober\AppData\Local\Programs\Python\Python313\tcl\tcl8.6
    set TK_LIBRARY=C:\Users\Rober\AppData\Local\Programs\Python\Python313\tcl\tk8.6


6. Run the application:
   ```bash
   python src/ui.py
   ```

### Deactivating the Virtual Environment
When done working on the project:
```bash
deactivate
```

### Descripción Técnica del Analizador Sintáctico

#### Arquitectura del Parser
El analizador sintáctico está implementado mediante un enfoque de descenso recursivo, donde cada regla de la gramática se traduce a un método específico. El parser recibe una lista de tokens generados por el analizador léxico y construye un Árbol de Sintaxis Abstracta (AST) que representa la estructura del programa fuente.

#### Clases Principales

1. **Parser**: Clase principal que coordina el proceso de análisis.
   - Recibe una lista de tokens del analizador léxico
   - Proporciona métodos para consumir tokens y manejar errores
   - Implementa el método `parse()` que inicia el proceso de análisis

2. **ASTNode y Subclases**: Jerarquía de nodos para construir el AST.
   - `ASTNode`: Clase base con tipo, valor, línea, columna y lista de hijos
   - Subclases especializadas para cada construcción sintáctica (ej. `ProgramNode`, `IfNode`, `BinaryOpNode`, etc.)

#### Características Implementadas

1. **Análisis de Estructura**: El parser analiza la estructura completa del programa, incluyendo:
   - Declaraciones de variables
   - Asignaciones
   - Operaciones aritméticas y lógicas
   - Estructuras de control (if-else, while, do-until)
   - Entrada/salida (cin, cout)

2. **Manejo de Errores**: Implementa estrategias de recuperación de errores para continuar el análisis después de encontrar problemas sintácticos.

3. **Transformación de Incrementos Post-fijos**:
   - Las expresiones de incremento/decremento post-fijo (`a++`, `a--`) son transformadas en operaciones de asignación equivalentes (`a = a + 1`, `a = a - 1`)
   - Esta transformación facilita etapas posteriores de análisis y generación de código

4. **Visualización del AST**: 
   - El AST generado es visualizado en una estructura de árbol expandible
   - Se muestran detalles como tipo de nodo, valor, línea y columna
   - Operadores convertidos a nombres descriptivos (ej. '+' → 'PLUS')

#### Flujo de Ejecución

1. El método `parse()` inicia el análisis llamando a `parse_program()`
2. Cada regla de la gramática tiene su correspondiente método `parse_*()` 
3. Los métodos consumen tokens según lo requerido y crean nodos AST
4. Los nodos se conectan formando una estructura jerárquica
5. Al finalizar, se retorna el nodo raíz del AST junto con los errores encontrados

#### Implementación de la Gramática

La gramática del lenguaje se implementa mediante métodos recursivos que siguen su estructura EBNF:

```
program → main { lista_declaracion }
lista_declaracion → declaracion { declaracion }
declaracion → declaracion_variable | lista_sentencias
declaracion_variable → tipo identificador ;
// ... (resto de reglas gramaticales)
```

Cada regla se traduce a un método que construye la porción correspondiente del AST.

### Programas de Prueba

Se han incluido varios programas de prueba en el directorio `examples/` para verificar el correcto funcionamiento del compilador:

1. **Operaciones Aritméticas** (`arithmetic_operations.txt`):
   - Prueba de operadores aritméticos (+, -, *, /, %)
   - Verificación de precedencia de operadores
   - Manejo de expresiones complejas con paréntesis

2. **Condicionales y Operaciones Booleanas** (`conditionals_and_booleans.txt`):
   - Estructuras if-else simples y anidadas
   - Operadores lógicos (&&, ||)
   - Variables y literales booleanos

3. **Bucles e Incrementos** (`loops_and_increments.txt`):
   - Bucles while y do-until
   - Operaciones de post-incremento (i++, i--)
   - Transformación de incrementos a asignaciones en el AST
   - Bucles anidados

4. **Entrada/Salida** (`input_output.txt`):
   - Operaciones de entrada con cin
   - Operaciones de salida con cout
   - Secuencias de entrada/salida

5. **Prueba Comprehensiva** (`comprehensive_test.txt`):
   - Programa completo con múltiples características
   - Algoritmo para verificar si un número es primo
   - Cálculo de factorial y secuencia Fibonacci
   - Combinación de todas las estructuras del lenguaje

6. **Casos Límite** (`edge_cases.txt`):
   - Construcciones inusuales y casos extremos
   - Declaraciones múltiples
   - Valores especiales (cero, negativos)
   - Estructuras vacías
   - Expresiones altamente anidadas

7. **Detección de Errores** (`syntax_errors.txt`):
   - Contiene 30 ejemplos de errores sintácticos comunes
   - Prueba la capacidad del parser para detectar y reportar errores
   - Incluye errores como:
     - Símbolos de apertura/cierre faltantes
     - Estructura if-then-end incompleta
     - Paréntesis desbalanceados
     - Operadores sin operandos
     - Declaraciones y sentencias incompletas
     - Estructuras de control malformadas
   - Útil para verificar la robustez del analizador sintáctico

Para ejecutar estos programas:
1. Abra el IDE del compilador: `python main.py`
2. Abra uno de los archivos de ejemplo
3. Ejecute el análisis sintáctico para visualizar el AST
4. Observe cómo se representan las diferentes estructuras en el árbol

### Detección de Errores

El analizador sintáctico implementa un robusto sistema de detección de errores sintácticos. Para una documentación detallada de los tipos de errores que puede detectar, con ejemplos concretos de cada uno, consulte:

- [Errores Detectables por el Analizador Sintáctico](docs/errores_detectables.md)

Además, puede encontrar ejemplos de errores en los siguientes archivos:

- `examples/errors_structure.txt` - Errores de estructura del programa
- `examples/errors_declarations.txt` - Errores en declaraciones de variables
- `examples/errors_assignments.txt` - Errores en sentencias y asignaciones
- `examples/errors_control_structures.txt` - Errores en estructuras de control

El analizador reporta estos errores de manera clara, indicando la línea y columna donde se detectó el problema, lo que facilita la corrección del código fuente. El archivo `examples/syntax_errors.txt` contiene ejemplos de todos estos tipos de errores para probar la capacidad de detección.