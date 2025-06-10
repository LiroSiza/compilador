#!/usr/bin/env python3
"""
Test the line number logic without GUI
"""

def test_line_number_logic():
    """Test line number calculation logic"""
    
    # Test case 1: Basic multi-line text
    test_text1 = """main {
    int x, y;
    x = 5 + 3;
    y = x * 2;
}"""
    
    # Simulate the logic from update_line_numbers
    text_content = test_text1  # This would be text_area.get('1.0', 'end-1c')
    
    if not text_content:
        expected_lines = 1
        line_numbers_text = '  1'
    else:
        lines = text_content.split('\n')
        num_lines = len(lines)
        line_numbers_text = '\n'.join(str(i).rjust(3) for i in range(1, num_lines + 1))
        expected_lines = num_lines
    
    actual_line_numbers = line_numbers_text.split('\n')
    text_lines = text_content.split('\n')
    
    print("TEST 1: Basic multi-line text")
    print(f"Text content:\n{test_text1}")
    print(f"Text lines: {len(text_lines)}")
    print(f"Expected line numbers: {expected_lines}")
    print(f"Generated line numbers: {len(actual_line_numbers)}")
    print(f"Line numbers: {line_numbers_text}")
    
    test1_pass = len(actual_line_numbers) == len(text_lines)
    print(f"Test 1 Result: {'PASS' if test1_pass else 'FAIL'}\n")
    
    # Test case 2: Empty text
    test_text2 = ""
    
    text_content = test_text2
    if not text_content:
        expected_lines = 1
        line_numbers_text = '  1'
    else:
        lines = text_content.split('\n')
        num_lines = len(lines)
        line_numbers_text = '\n'.join(str(i).rjust(3) for i in range(1, num_lines + 1))
        expected_lines = num_lines
    
    print("TEST 2: Empty text")
    print(f"Text content: '{test_text2}'")
    print(f"Generated line numbers: {line_numbers_text}")
    print(f"Expected: Single line number '1'")
    
    test2_pass = line_numbers_text == '  1'
    print(f"Test 2 Result: {'PASS' if test2_pass else 'FAIL'}\n")
    
    # Test case 3: Text with trailing newlines
    test_text3 = """main {
    int x;
    x++;
}
"""
    
    text_content = test_text3.rstrip('\n')  # This simulates 'end-1c' behavior
    if not text_content:
        expected_lines = 1
        line_numbers_text = '  1'
    else:
        lines = text_content.split('\n')
        num_lines = len(lines)
        line_numbers_text = '\n'.join(str(i).rjust(3) for i in range(1, num_lines + 1))
        expected_lines = num_lines
    
    actual_line_numbers = line_numbers_text.split('\n')
    text_lines = text_content.split('\n')
    
    print("TEST 3: Text with trailing newlines")
    print(f"Original text: {repr(test_text3)}")
    print(f"Processed text: {repr(text_content)}")
    print(f"Text lines: {len(text_lines)}")
    print(f"Generated line numbers: {len(actual_line_numbers)}")
    print(f"Line numbers: {line_numbers_text}")
    
    test3_pass = len(actual_line_numbers) == len(text_lines)
    print(f"Test 3 Result: {'PASS' if test3_pass else 'FAIL'}\n")
    
    # Overall result
    all_tests_pass = test1_pass and test2_pass and test3_pass
    
    print("="*50)
    print("LINE NUMBER LOGIC TEST SUMMARY")
    print("="*50)
    print(f"Test 1 (Multi-line): {'PASS' if test1_pass else 'FAIL'}")
    print(f"Test 2 (Empty): {'PASS' if test2_pass else 'FAIL'}")  
    print(f"Test 3 (Trailing newlines): {'PASS' if test3_pass else 'FAIL'}")
    print(f"Overall: {'ALL TESTS PASSED' if all_tests_pass else 'SOME TESTS FAILED'}")
    
    if all_tests_pass:
        print("\n✓ Line number calculation logic is working correctly!")
        print("✓ Line numbers should now align properly with text lines.")
    else:
        print("\n❌ Line number calculation has issues that need fixing.")
    
    print("="*50)
    
    return all_tests_pass

if __name__ == "__main__":
    test_line_number_logic()
