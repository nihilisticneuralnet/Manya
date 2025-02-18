import tempfile
import os
from pathlib import Path
import shutil
import sys
from contextlib import contextmanager
import re

def extract_code(response):
    """Extract code from model response"""
    code_lines = []
    in_code_block = False
    for line in response.split('\n'):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_lines.append(line)
    return '\n'.join(code_lines)

def _extract_scene_name(self, code):
    """Extract the Scene class name from the code"""
    import re
    # Look for class definitions that end with 'Scene'
    pattern = r"class\s+(\w+Scene)\s*\("
    matches = re.findall(pattern, code)
    return matches[-1] if matches else None

@contextmanager
def _create_temp_dir(self):
    """Context manager for creating and cleaning up temporary directory"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
