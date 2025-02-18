from smolagents import HfApiModel, CodeAgent, ManagedAgent
import subprocess
import tempfile
import os
from pathlib import Path
import shutil
import sys
from contextlib import contextmanager
import re
from executor import ManimExecutorAgent
# from executor2 import ManimExecutorAgent
from coder import ManimCodeWriterAgent
from depender import DependencyManager



class ManimManagerAgent(ManagedAgent):
    """Manager agent that coordinates the animation creation process"""
    
    def __init__(self, model):
        # First, ensure dependencies are installed
        if not DependencyManager.install_dependencies():
            raise RuntimeError("Failed to install required dependencies")
            
        self.writer = ManimCodeWriterAgent(model)
        self.executor = ManimExecutorAgent(model)
        
        super().__init__(
            agent=CodeAgent(
                tools=[],
                model=model,
                managed_agents=[self.writer, self.executor]
            ),
            name="manim_manager",
            description="Manages the creation of educational animations using Manim"
        )
    
    def create_animation(self, concept):
        """Coordinate the creation of a Manim animation for the given concept"""
        # Step 1: Generate the code
        code = self.writer.generate_code(concept)
        
        # Step 2: Execute and debug if necessary
        video_path = self.executor.execute_code(code)
        
        return video_path