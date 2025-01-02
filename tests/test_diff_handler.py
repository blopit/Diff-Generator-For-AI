from __future__ import print_function
import unittest
import sys
import os
from diff_handler import extract_code_blocks, generate_diff, apply_diff, process_ai_output, parse_code_block

class TestDiffHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data paths"""
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    
    def read_test_file(self, example_dir, filename):
        """Helper to read test data files"""
        path = os.path.join(self.test_data_dir, example_dir, filename)
        with open(path, 'r') as f:
            return f.read()

    def test_extract_code_blocks(self):
        ai_output = self.read_test_file('example1', 'ai_output.md')
        blocks = extract_code_blocks(ai_output)
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.language, 'python')
        self.assertEqual(block.filepath, 'example.py')
        self.assertEqual(block.content, '// existing code...\nprint("Hello, World!")\n// ...')

    def test_generate_diff(self):
        original_code = self.read_test_file('example1', 'original.py')
        new_code = self.read_test_file('example1', 'modified.py')
        expected_diff = "--- Original\n+++ Modified\n@@ -1 +1 @@\n-print('Hello')\n+print('Hello, World!')\n"
        diff = generate_diff(original_code, new_code)
        self.assertEqual(diff, expected_diff)

    def test_apply_diff(self):
        original_code = self.read_test_file('example1', 'original.py')
        new_code = self.read_test_file('example1', 'modified.py')
        modified_code = apply_diff(original_code, new_code)
        self.assertEqual(modified_code.strip(), new_code.strip())

    def test_process_ai_output(self):
        ai_output = self.read_test_file('example1', 'ai_output.md')
        original_code = self.read_test_file('example1', 'original.py')
        expected_code = self.read_test_file('example1', 'modified.py')
        
        files = {'example.py': original_code}
        expected_files = {'example.py': expected_code}
        modified_files = process_ai_output(ai_output, files)
        self.assertEqual(modified_files, expected_files)

    def test_parse_code_block_with_markers(self):
        """Test parsing code blocks with various context markers"""
        block_content = self.read_test_file('markers', 'input.py')
        expected_content = self.read_test_file('markers', 'expected.py')
        
        changes = parse_code_block(block_content)
        self.assertEqual(len(changes), 1)
        
        action, content, context = changes[0]
        self.assertEqual(action, 'replace')
        self.assertEqual(content.strip(), expected_content.strip())
        self.assertEqual(context, 3)

    def test_parse_code_block_multiple_sections(self):
        """Test parsing code blocks with multiple changed sections"""
        block_content = self.read_test_file('multiple_sections', 'input.py')
        expected_sections = [
            self.read_test_file('multiple_sections', 'section1.py'),
            self.read_test_file('multiple_sections', 'section2.py')
        ]
        
        changes = parse_code_block(block_content)
        self.assertEqual(len(changes), 2)
        
        for i, (action, content, context) in enumerate(changes):
            self.assertEqual(action, 'replace')
            self.assertEqual(content.strip(), expected_sections[i].strip())

    def test_apply_diff_with_context(self):
        """Test applying changes with proper context matching"""
        original_code = self.read_test_file('example2', 'original.py')
        new_content = self.read_test_file('example2', 'modified.py')
        expected_code = self.read_test_file('example2', 'expected.py')
        
        modified_code = apply_diff(original_code, new_content)
        self.assertEqual(modified_code.strip(), expected_code.strip())

if __name__ == '__main__':
    unittest.main() 