#!/usr/bin/env python3
"""
Test script for semantic analyzer reference tracking
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

def test_reference_tracking():
    """Test that symbol table correctly tracks multiple references to the same variable"""

    # Code with multiple references to x in the same expression
    code = """
main {
    int x;
    x = 5;
    x = x + 23;
}
"""

    print("Testing reference tracking for expression: x = x + 23")
    print("=" * 50)

    # Lexical analysis
    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(code)

    if lex_errors:
        print("❌ Lexical errors found:")
        for error in lex_errors:
            print(f"  - {error}")
        return False

    print(f"✓ Generated {len(tokens)} tokens")

    # Parsing
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()

    if parse_errors:
        print("❌ Parse errors found:")
        for error in parse_errors:
            print(f"  - {error}")
        return False

    print("✓ AST constructed successfully")

    # Semantic analysis
    analyzer = SemanticAnalyzer(ast)
    annotated_ast, errors = analyzer.analyze()

    if errors:
        print("❌ Semantic errors found:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✓ Semantic analysis completed")

    # Check symbol table references
    print("\nSymbol Table References:")
    print("-" * 30)

    # Get references for variable x
    x_entry = analyzer.symbol_table.lookup("x")
    if x_entry:
        print(f"Variable 'x': declared at line {x_entry.declaration_line}, type: {x_entry.type}")
        print(f"References: {x_entry.lines}")

        # Should have multiple references: declaration + assignment target + expression references
        # In 'x = x + 23': x appears in declaration (line 3), assignment target (line 5), and in expression (line 5)
        expected_refs = 4  # declaration (1) + assignment target (1) + expression references (2)
        if len(x_entry.lines) == expected_refs:
            print(f"✓ Correct number of references: {expected_refs} (declaration + assignment + 2 expression refs)")
            return True
        else:
            print(f"❌ Expected {expected_refs} references, got {len(x_entry.lines)}")
            print(f"   References: {x_entry.lines}")
            return False
    else:
        print("❌ Variable 'x' not found in symbol table")
        return False

if __name__ == "__main__":
    success = test_reference_tracking()
    if success:
        print("\n🎉 Reference tracking test PASSED!")
    else:
        print("\n❌ Reference tracking test FAILED!")
        sys.exit(1)