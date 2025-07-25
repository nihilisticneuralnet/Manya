import os
import logging
import tempfile
import shutil
import sys
import importlib.util
import re
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path

def setup_logging(level: int = logging.INFO, 
                 log_file: Optional[str] = None,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration for the animation system
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    logger = logging.getLogger('manim_animation_system')
    logger.setLevel(level)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        ensure_directory_exists(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def ensure_directory_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        directory: Path to directory to create
    """
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logging.getLogger('manim_animation_system').info(f"Created directory: {directory}")
        except OSError as e:
            logging.getLogger('manim_animation_system').error(f"Failed to create directory {directory}: {e}")
            raise

def extract_code_from_response(response: str) -> str:
    """
    Extract Python code from LLM response that may contain markdown or other formatting
    
    Args:
        response: Raw response text from LLM
    
    Returns:
        Extracted Python code as string
    """
    # try to extract code from python markdown blocks
    python_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
    if python_blocks:
        return python_blocks[0].strip()
    
    # try to extract code from generic markdown blocks
    generic_blocks = re.findall(r'```\n(.*?)\n```', response, re.DOTALL)
    if generic_blocks:
        code_candidate = generic_blocks[0].strip()
        if looks_like_python_code(code_candidate):
            return code_candidate
    
    # try to extract code from single backtick blocks
    single_tick_blocks = re.findall(r'`([^`]*class[^`]*Scene[^`]*)`', response, re.DOTALL)
    if single_tick_blocks:
        return single_tick_blocks[0].strip()
    
    # Last resort: return the whole response if it looks like Python code
    if looks_like_python_code(response):
        return response.strip()
    
    return ""

def looks_like_python_code(text: str) -> bool:
    """
    Check if text looks like Python code based on common patterns
    
    Args:
        text: Text to analyze
    
    Returns:
        True if text appears to be Python code
    """
    python_indicators = [
        r'class\s+\w+.*:',
        r'def\s+\w+.*:',
        r'import\s+\w+',
        r'from\s+\w+\s+import',
        r'self\.',
        r'Scene',
        r'construct'
    ]
    
    text_lower = text.lower()
    matches = sum(1 for pattern in python_indicators if re.search(pattern, text, re.IGNORECASE))
    
    return matches >= 2

def extract_scene_name(code: str) -> Optional[str]:
    """
    Extract the scene class name from Manim Python code
    
    Args:
        code: Python code containing Manim scene class
    
    Returns:
        Scene class name if found, None otherwise
    """
    scene_patterns = [
        r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*Scene[^)]*\)\s*:',
        r'class\s+([A-Za-z_][A-Za-z0-9_]*Scene[A-Za-z0-9_]*)\s*\([^)]*\)\s*:',
        r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*Scene\s*\)\s*:'
    ]
    
    for pattern in scene_patterns:
        matches = re.findall(pattern, code)
        if matches:
            return matches[0]
    
    return None

def format_previous_attempts(attempts: List[Dict[str, Any]]) -> str:
    """
    Format previous debugging attempts for context in error messages
    
    Args:
        attempts: List of previous attempt results
    
    Returns:
        Formatted string describing previous attempts
    """
    if not attempts:
        return "No previous attempts."
    
    formatted_lines = []
    for i, attempt in enumerate(attempts, 1):
        formatted_lines.append(f"Attempt {i}:")
        
        if hasattr(attempt, 'error_type'):
            formatted_lines.append(f"  Error Type: {attempt.error_type}")
        elif 'error_type' in attempt:
            formatted_lines.append(f"  Error Type: {attempt['error_type']}")
        
        if hasattr(attempt, 'error'):
            error_msg = str(attempt.error)[:200] + "..." if len(str(attempt.error)) > 200 else str(attempt.error)
            formatted_lines.append(f"  Error: {error_msg}")
        elif 'error' in attempt:
            error_msg = str(attempt['error'])[:200] + "..." if len(str(attempt['error'])) > 200 else str(attempt['error'])
            formatted_lines.append(f"  Error: {error_msg}")
        
        if hasattr(attempt, 'fixes_applied') and attempt.fixes_applied:
            formatted_lines.append(f"  Fixes Applied: {', '.join(attempt.fixes_applied)}")
        elif 'fixes_applied' in attempt and attempt['fixes_applied']:
            formatted_lines.append(f"  Fixes Applied: {', '.join(attempt['fixes_applied'])}")
        
        formatted_lines.append("")  
    
    return "\n".join(formatted_lines)

@contextmanager
def create_temp_dir(prefix: str = "manim_temp_", cleanup: bool = True):
    """
    Context manager for creating temporary directories
    
    Args:
        prefix: Prefix for temporary directory name
        cleanup: Whether to clean up directory on exit
    
    Yields:
        Path to temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    logger = logging.getLogger('manim_animation_system')
    
    try:
        logger.debug(f"Created temporary directory: {temp_dir}")
        yield temp_dir
    finally:
        if cleanup:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")

def validate_python_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Python code syntax without executing it
    
    Args:
        code: Python code to validate
    
    Returns:
        Dictionary with validation results
    """
    try:
        compile(code, '<string>', 'exec')
        return {
            "valid": True,
            "error": None,
            "error_type": None
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": str(e),
            "error_type": "syntax_error",
            "line_number": e.lineno,
            "offset": e.offset
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "error_type": "compilation_error"
        }

def clean_code_indentation(code: str, indent_size: int = 4) -> str:
    """
    Clean and standardize code indentation
    
    Args:
        code: Python code to clean
        indent_size: Number of spaces for each indentation level
    
    Returns:
        Code with standardized indentation
    """
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.expandtabs(indent_size)
        
        stripped = line.lstrip()
        if stripped:  
            original_indent = len(line) - len(stripped)
            indent_level = original_indent // indent_size
            proper_indent = ' ' * (indent_level * indent_size)
            cleaned_lines.append(proper_indent + stripped)
        else:
            cleaned_lines.append('')  
    
    return '\n'.join(cleaned_lines)

def extract_imports_from_code(code: str) -> List[str]:
    """
    Extract import statements from Python code
    
    Args:
        code: Python code to analyze
    
    Returns:
        List of import statements found
    """
    import_patterns = [
        r'^import\s+[\w\.,\s]+',
        r'^from\s+[\w\.]+\s+import\s+[\w\.,\s\*]+'
    ]
    
    imports = []
    for line in code.split('\n'):
        line = line.strip()
        for pattern in import_patterns:
            if re.match(pattern, line):
                imports.append(line)
                break
    
    return imports

def get_file_extension_from_mime(mime_type: str) -> str:
    """
    Get file extension from MIME type
    
    Args:
        mime_type: MIME type string
    
    Returns:
        File extension including dot
    """
    mime_map = {
        'video/mp4': '.mp4',
        'audio/wav': '.wav',
        'audio/mpeg': '.mp3',
        'text/plain': '.txt',
        'application/python': '.py',
        'image/png': '.png',
        'image/jpeg': '.jpg'
    }
    
    return mime_map.get(mime_type, '.txt')

def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create a safe filename by removing/replacing problematic characters
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
    
    Returns:
        Safe filename
    """
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_chars = re.sub(r'\s+', '_', safe_chars) 
    safe_chars = re.sub(r'_+', '_', safe_chars)  
    
    if len(safe_chars) > max_length:
        name, ext = os.path.splitext(safe_chars)
        max_name_length = max_length - len(ext)
        safe_chars = name[:max_name_length] + ext
    
    return safe_chars.strip('_')

def get_project_root() -> Path:
    """
    Get the root directory of the project
    
    Returns:
        Path object pointing to project root
    """
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / 'main.py').exists() or (parent / 'requirements.txt').exists():
            return parent
    
    return current_file.parent

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(remaining_minutes)}m"

def estimate_speech_duration(text: str, words_per_minute: int = 150) -> float:
    """
    Estimate speech duration for given text
    
    Args:
        text: Text to analyze
        words_per_minute: Speaking rate in words per minute
    
    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    
    duration_minutes = word_count / words_per_minute
    return duration_minutes * 60

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_error_message(error_message: str) -> Dict[str, Any]:
    """
    Parse error message to extract useful information
    
    Args:
        error_message: Raw error message string
    
    Returns:
        Dictionary with parsed error information
    """
    error_info = {
        "type": "unknown",
        "message": error_message,
        "line_number": None,
        "file": None,
        "suggestions": []
    }
    
    # common error patterns
    patterns = {
        "syntax_error": r"SyntaxError: (.+)",
        "indentation_error": r"IndentationError: (.+)",
        "name_error": r"NameError: (.+)",
        "attribute_error": r"AttributeError: (.+)",
        "type_error": r"TypeError: (.+)",
        "import_error": r"(ImportError|ModuleNotFoundError): (.+)"
    }
    
    for error_type, pattern in patterns.items():
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            error_info["type"] = error_type
            error_info["message"] = match.group(1) if len(match.groups()) == 1 else match.group(2)
            break
    
    line_match = re.search(r"line (\d+)", error_message, re.IGNORECASE)
    if line_match:
        error_info["line_number"] = int(line_match.group(1))
    
    file_match = re.search(r"File \"([^\"]+)\"", error_message)
    if file_match:
        error_info["file"] = file_match.group(1)
    
    return error_info

# Initialize module logger
logger = logging.getLogger('manim_animation_system.utils')
