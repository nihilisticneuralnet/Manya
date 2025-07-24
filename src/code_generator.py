from langchain.prompts import ChatPromptTemplate
from base_agent import BaseAgent
from rag_agent import RAGRouterAgent
from models import AgentType, IterationResult
from utils import extract_code_from_response, format_previous_attempts
import re

class CodeGeneratorAgent(BaseAgent):
    """Agent responsible for generating Manim code"""
    
    def __init__(self, llm: ChatGroq, rag_agent: RAGRouterAgent):
        super().__init__("Code Generator", llm, AgentType.CODE_GENERATOR)
        self.rag_agent = rag_agent
        
        # Error patterns for debugging
        self.error_patterns = {
            'indentation': r'IndentationError|unexpected indent|expected an indented block',
            'syntax': r'SyntaxError|invalid syntax|unexpected token',
            'unbound_local': r'UnboundLocalError|local variable.*referenced before assignment',
            'name_error': r'NameError|name.*is not defined',
            'import_error': r'ImportError|ModuleNotFoundError|No module named',
            'attribute_error': r'AttributeError|has no attribute',
            'type_error': r'TypeError|unsupported operand type|takes.*positional arguments',
            'manim_specific': r'Scene.*not found|construct.*method|Animation.*error'
        }
        
        self.debug_templates = {
            'indentation': """
The following Manim code has an IndentationError:

CODE:
{code}

ERROR:
{error}

PREVIOUS ATTEMPTS:
{previous_attempts}

Please fix the indentation issues and return only the corrected Python code. Make sure to:
1. Use exactly 4 spaces for each indentation level
2. Ensure proper class and method indentation
3. Check that all code blocks are properly indented
4. Verify that there are no mixing of tabs and spaces

Fixed code:
""",
            'general': """
The following Manim code has an error:

CODE:
{code}

ERROR:
{error}

PREVIOUS ATTEMPTS:
{previous_attempts}

Please analyze the error carefully and fix the code. Return only the corrected Python code. Make sure to:
1. Fix the specific error mentioned
2. Use proper Manim Community v0.17+ syntax
3. Include all necessary imports
4. Ensure the Scene class is properly defined
5. Avoid making the same mistakes from previous attempts

Fixed code:
"""
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate initial Manim code"""
        request = input_data['request']
        scene_outline = input_data.get('scene_outline', '')
        
        logger.info(f"💻 Generating Manim code for: {request.description}")
        
        # Get relevant context
        rag_result = self.rag_agent.process({'query': request.description})
        context = rag_result['context']
        
        code_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Manim developer. Generate clean, executable Python code for educational animations. 

CRITICAL RULES:
1. Always use exactly 4 spaces for indentation (never tabs)
2. Always include 'from manim import *' at the top
3. Always implement the construct method
4. Initialize all variables before using them
5. Use proper Manim Community v0.17+ syntax
6. Test your code mentally before outputting

TEMPLATE TO FOLLOW:
```python
from manim import *

class AnimationScene(Scene):
    def construct(self):
        # Initialize all objects first
        # Then animate them
        # Use self.play() for animations
        # Use self.wait() for pauses
        pass
```"""),
            ("human", f"""
Generate complete, executable Manim Python code for: {request.description}

Requirements:
- Duration: {request.duration} seconds
- Style: {request.style}
- Complexity: {request.complexity}

Scene Outline:
{scene_outline}

Relevant Manim concepts:
{context}

Return ONLY the Python code, properly indented with 4 spaces, no explanations.
""")
        ])
        
        chain = code_prompt | self.llm
        response = chain.invoke({})
        
        # Extract and clean the code
        code = self.extract_code_from_response(response.content)
        if not code:
            code = response.content.strip()
        
        return {
            "code": code,
            "raw_response": response.content
        }
    
    def extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response"""
        # Try to extract code from markdown blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # Try to extract code from any code blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', response, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # Last resort: return the whole response if it looks like code
        if 'class' in response and 'def construct' in response:
            return response.strip()
        
        return ""
    
    def identify_error_type(self, error_message: str) -> str:
        """Identify the type of error based on error message"""
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return error_type
        return 'general'
    
    def debug_code(self, code: str, error: str, previous_attempts: List[IterationResult] = None) -> str:
        """Debug code based on error"""
        error_type = self.identify_error_type(error)
        template = self.debug_templates.get(error_type, self.debug_templates['general'])
        
        previous_attempts_text = self.format_previous_attempts(previous_attempts or [])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Python and Manim developer. Fix the code errors and provide a corrected version."),
            ("human", template.format(
                code=code,
                error=error,
                previous_attempts=previous_attempts_text
            ))
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return self.extract_code_from_response(response.content)
    
    def format_previous_attempts(self, attempts: List[IterationResult]) -> str:
        """Format previous attempts for context"""
        if not attempts:
            return "No previous attempts."
        
        formatted = []
        for attempt in attempts:
            formatted.append(f"Attempt {attempt.iteration}:")
            formatted.append(f"  Error Type: {attempt.error_type}")
            formatted.append(f"  Error: {attempt.error}")
            formatted.append("")
        
        return "\n".join(formatted)