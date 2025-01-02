from __future__ import print_function
import difflib
import re
import sys

# Check Python version for compatibility
PY2 = sys.version_info[0] == 2

if not PY2:
    from typing import List, Tuple, Optional, Dict
    from dataclasses import dataclass
    
    @dataclass
    class CodeBlock:
        language: str
        filepath: Optional[str]
        content: str
else:
    # Python 2 compatible CodeBlock class
    class CodeBlock(object):
        def __init__(self, language, filepath, content):
            self.language = language
            self.filepath = filepath
            self.content = content
        
        def __eq__(self, other):
            if not isinstance(other, CodeBlock):
                return False
            return (self.language == other.language and 
                    self.filepath == other.filepath and 
                    self.content == other.content)

def extract_code_blocks(ai_output):
    """
    Extract code blocks from markdown-formatted AI output.
    Returns a list of CodeBlock objects containing language, filepath, and content.
    """
    code_block_pattern = r'```(\w+)(?::([^\n]+))?\n(.*?)```'
    matches = re.finditer(code_block_pattern, ai_output, re.DOTALL)
    
    code_blocks = []
    for match in matches:
        language = match.group(1)
        filepath = match.group(2)  # May be None
        content = match.group(3).strip()
        code_blocks.append(CodeBlock(language, filepath, content))
    
    return code_blocks

def parse_code_block(block_content):
    """
    Parse a code block to identify changes.
    Returns list of tuples: (action, content, context_lines)
    """
    changes = []
    lines = block_content.splitlines()
    current_section = []
    in_change_section = False
    
    # Common markers used by AI to indicate unchanged code
    context_markers = {
        '// existing code...',
        '// ...',
        '# existing code...',
        '# ...',
        '...',
        '# rest of the file',
        '// rest of the file',
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped in context_markers:
            if in_change_section and current_section:
                # End of a change section, save the accumulated changes
                changes.append(('replace', '\n'.join(current_section), 3))
                current_section = []
            in_change_section = False
        else:
            # This is actual code to be changed
            in_change_section = True
            current_section.append(line)
    
    # Don't forget any remaining changes
    if current_section:
        changes.append(('replace', '\n'.join(current_section), 3))
    
    return changes

def generate_diff(original_code, new_code, context_lines=3):
    """Generate a unified diff between original and new code."""
    diff = difflib.unified_diff(
        original_code.splitlines(),
        new_code.splitlines(),
        fromfile='Original',
        tofile='Modified',
        n=context_lines,
        lineterm=''
    )
    return '\n'.join(diff)

def apply_diff(original_code, new_content):
    """
    Apply changes to the original code by matching context and content.
    """
    original_lines = original_code.splitlines()
    new_lines = new_content.splitlines()
    result_lines = original_lines[:]
    
    # Find the matching position for the new content
    for i in range(len(original_lines)):
        # Try to match the content at this position
        match_found = False
        for j in range(len(new_lines)):
            if new_lines[j] in original_lines[i:i+len(new_lines)]:
                # Found a matching line, this might be the right position
                match_found = True
                # Replace the content at this position
                result_lines[i:i+len(new_lines)] = new_lines
                break
        if match_found:
            break
    
    return '\n'.join(result_lines)

def process_ai_output(ai_output, files):
    """
    Process AI output and apply changes to multiple files.
    """
    modified_files = files.copy()
    code_blocks = extract_code_blocks(ai_output)
    
    for block in code_blocks:
        if not block.filepath:
            continue
            
        if block.filepath not in modified_files:
            # New file
            modified_files[block.filepath] = block.content
            continue
            
        original_content = modified_files[block.filepath]
        changes = parse_code_block(block.content)
        
        # Apply each change section
        current_content = original_content
        for action, content, context in changes:
            if action == 'replace':
                current_content = apply_diff(current_content, content)
        
        modified_files[block.filepath] = current_content
    
    return modified_files

if __name__ == "__main__":
    # Example usage
    ai_output = '''
Here's how to fix the authentication endpoint:

```python:auth.py
// existing imports...
from fastapi.security import OAuth2PasswordBearer
// ...

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
// rest of the file...
```
    '''
    
    files = {
        'auth.py': '''
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
'''
    }
    
    modified_files = process_ai_output(ai_output, files)
    
    # Print the changes
    for filepath, content in modified_files.items():
        print("\nModified {}:".format(filepath))
        print(content)
