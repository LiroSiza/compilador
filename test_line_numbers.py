#!/usr/bin/env python3
"""
Test script to verify line number alignment in the IDE
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import tkinter as tk
    from src.ui import IDE
    
    def test_line_numbers():
        """Test that line numbers are working correctly"""
        print("Testing line number alignment...")
        
        root = tk.Tk()
        root.withdraw()  # Hide the main window for testing
        
        ide = IDE(root)
        
        # Test with some sample text
        test_text = """main {
    int x, y;
    x = 5 + 3;
    y = x * 2;
    
    if x > y then
        cout << x;
    else
        cout << y;
    end
    
    while x > 0
        x = x - 1;
    end
}"""
        
        # Insert test text
        ide.text_area.insert(tk.END, test_text)
        
        # Update line numbers
        ide.update_line_numbers()
        
        # Get line numbers content
        line_nums = ide.line_numbers.get('1.0', 'end-1c')
        text_content = ide.text_area.get('1.0', 'end-1c')
        
        # Count lines in both
        line_num_lines = line_nums.split('\n')
        text_lines = text_content.split('\n')
        
        print(f"Text lines: {len(text_lines)}")
        print(f"Line number lines: {len(line_num_lines)}")
        print(f"Line numbers: {line_nums}")
        
        if len(line_num_lines) == len(text_lines):
            print("✓ Line numbers are correctly aligned!")
            success = True
        else:
            print("❌ Line numbers are NOT aligned!")
            success = False
        
        root.destroy()
        return success
    
    if __name__ == "__main__":
        success = test_line_numbers()
        print("\n" + "="*50)
        if success:
            print("LINE NUMBER TEST PASSED!")
            print("The line numbers should now be properly aligned with the text.")
        else:
            print("LINE NUMBER TEST FAILED!")
        print("="*50)
        
except Exception as e:
    print(f"Test failed due to error: {e}")
    import traceback
    traceback.print_exc()
