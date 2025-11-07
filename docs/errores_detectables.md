# Errores Detectables por el Analizador Sintáctico

Este documento describe los tipos de errores que el analizador sintáctico puede detectar, junto con ejemplos concretos de cada uno.

## 1. Errores de Estructura del Programa

### Falta de la estructura `main`
```
// Error: No hay estructura main
{
    int x;
    x = 10;
}
```

### Llaves de apertura/cierre `{` `}` faltantes o desbalanceadas
```
// Error: Falta llave de apertura
main 
    int x;
    x = 10;
}

// Error: Falta llave de cierre
main {
    int x;
    x = 10;
```

### Múltiples definiciones de `main`
```
// Error: Múltiples bloques main
main {
    int x;
    x = 10;
}

main {
    int y;
    y = 20;
}
```

## 2. Errores en Declaraciones

### Punto y coma `;` faltante en declaraciones
```
// Error: Falta punto y coma
main {
    int x
    x = 10;
}
```

### Tipo de dato inválido o no reconocido
```
// Error: 'string' no es un tipo válido
main {
    string name;
    name = "John";
}
```

### Declaraciones incompletas (tipo sin identificador)
```
// Error: Declaración incompleta
main {
    int;
    x = 10;
}
```

### Declaración de variables después de sentencias ejecutables
```
// Error: Declaración después de sentencias
main {
    int x;
    x = 10;
    int y;  // No permitido aquí
}
```

## 3. Errores en Sentencias

### Punto y coma `;` faltante al final de sentencias
```
// Error: Falta punto y coma
main {
    int x;
    x = 10
}
```

### Uso de operadores de asignación incorrectos
```
// Error: ':=' no es un operador válido
main {
    int x;
    x := 10;
}
```

### Expresiones incompletas en asignaciones
```
// Error: Expresión de asignación incompleta
main {
    int x;
    x =;
}

// Error: Falta identificador
main {
    int x;
    = 10;
}
```

## 4. Errores en Estructuras de Control

### Palabra clave `then` faltante en estructuras `if`
```
// Error: Falta 'then'
main {
    int x;
    x = 10;
    if x > 5
        x = x + 1;
    end
}
```

### Palabra clave `end` faltante en estructuras `if`, `while`
```
// Error: Falta 'end' en if
main {
    int x;
    x = 10;
    if x > 5 then
        x = x + 1;
}

// Error: Falta 'end' en while
main {
    int x;
    x = 0;
    while x < 10
        x = x + 1;
}
```

### Palabra clave `until` faltante en estructuras `do-until`
```
// Error: Falta 'until'
main {
    int x;
    x = 10;
    do
        x = x - 1;
    x == 0;
}
```

### Condiciones faltantes en estructuras condicionales o repetitivas
```
// Error: Condición faltante en if
main {
    if then
        int x;
        x = 10;
    end
}

// Error: Condición faltante en while
main {
    while
        int x;
        x = 10;
    end
}

// Error: Condición faltante en until
main {
    do
        int x;
        x = 10;
    until;
}
```

## 5. Errores en Expresiones

### Paréntesis desbalanceados en expresiones
```
// Error: Paréntesis desbalanceados
main {
    int x;
    x = (5 + 3 * (2 - 1;
}
```

### Operadores binarios sin operando izquierdo o derecho
```
// Error: Falta operando derecho
main {
    int x;
    x = 5 + ;
}

// Error: Falta operando izquierdo
main {
    int x;
    x = * 5;
}
```

### Uso de operadores duplicados
```
// Error: Operadores duplicados
main {
    int x;
    x = 5 ++ 3;  // Uso incorrecto de ++
}
```

### Uso incorrecto de operadores unarios
```
// Error: Operador unario mal aplicado
main {
    int x;
    x = !5;  // Operador ! aplicado a un número
}
```

## 6. Errores en Incrementos/Decrementos

### Operadores de incremento/decremento aplicados a literales
```
// Error: Incremento aplicado a literal
main {
    5++;
}
```

### Operadores de incremento/decremento sin identificador
```
// Error: Incremento sin identificador
main {
    int x;
    ++;
}
```

## 7. Errores en Entrada/Salida

### Operadores `>>` o `<<` faltantes en instrucciones `cin` o `cout`
```
// Error: Falta operador >>
main {
    int x;
    cin x;
}

// Error: Falta operador <<
main {
    int x;
    cout x;
}
```

### Identificador faltante en operaciones de entrada
```
// Error: Falta identificador después de >>
main {
    cin >> ;
}
```

### Expresión faltante en operaciones de salida
```
// Error: Falta expresión después de <<
main {
    cout << ;
}
```

## 8. Errores Léxicos (detectados previamente)

### Caracteres no reconocidos
```
// Error: Carácter no reconocido @
main {
    int x;
    x = 5 @ 3;
}
```

### Números mal formateados
```
// Error: Número decimal mal formateado
main {
    float x;
    x = 5.;  // Falta dígito después del punto
}
```

### Comentarios sin cerrar
```
// Error: Comentario sin cerrar
main {
    int x;
    /* Este comentario no está cerrado
    x = 10;
}
```
