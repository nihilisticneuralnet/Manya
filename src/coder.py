from smolagents import HfApiModel, CodeAgent, ManagedAgent
import os
from pathlib import Path
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

class ManimCodeWriterAgent(ManagedAgent):
    """Agent responsible for converting educational concepts into Manim code"""
    
    def __init__(self, model):
        self.template = """
        You are an expert Manim programmer. Convert the following concept into production-ready Manim code:
        
        CONCEPT: {concept}
        
        REQUIREMENTS:
        1. Create an educational animation under 100 seconds
        2. Use ManimCE syntax version 0.17.3
        3. Include proper documentation and comments throughout the code
        4. Use meaningful variable names and follow PEP 8 style guidelines
        5. Implement smooth transitions and animations with appropriate timing
        6. Keep the scenes visually clear and avoid cluttering the screen
        7. Use color schemes that are easy on the eyes and accessible
        8. Include a proper title and labels where appropriate
        
        CODE STRUCTURE:
        - Start with: from manim import *
        - Create ONE main Scene class that ends with 'Scene' (e.g., BinarySearchScene)
        - Break complex animations into separate methods for better readability
        - Initialize all necessary objects and configurations in the constructor
        - Handle edge cases and potential errors gracefully
        
        OPTIMIZATION GUIDELINES:
        - Use appropriate Manim methods rather than reinventing functionality
        - Leverage existing Manim objects and animations when possible
        - Minimize redundant code and hardcoded values
        - Use numpy for efficient mathematical operations
        - Cache calculations when appropriate to avoid redundant computation
        
        Return ONLY the complete, runnable Python code without any explanation.
        """
        
        super().__init__(
            agent=CodeAgent(
                tools=[],
                model=model,
                additional_authorized_imports=["manim", "numpy", "math"]
            ),
            name="manim_writer",
            description="Writes Manim code for educational animations"
        )
    
    def generate_code(self, concept):
        """Generate Manim code for the given concept"""
        prompt = self.template.format(concept=concept)
        response = self.agent.run(prompt)
        return extract_code(response)