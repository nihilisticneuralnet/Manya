from smolagents import HfApiModel, CodeAgent, ManagedAgent
import subprocess
import tempfile
import os
from pathlib import Path
import shutil
import sys
from contextlib import contextmanager
import re
from executor1 import ManimProcessor

class ManimExecutorAgent(ManagedAgent):
    """Agent responsible for executing and debugging Manim code"""
    def __init__(self, model):
        self.debug_template = """
        You are an expert Manim debugger. Fix the following code that produced an error:
        
        ORIGINAL CODE:
        ```python
        {code}
        ```
        
        ERROR MESSAGE:
        ```
        {error}
        ```
        
        DEBUGGING INSTRUCTIONS:
        1. Carefully analyze the error message and identify the root cause
        2. Look for common Manim pitfalls like:
           - Incorrect object creation or parameters
           - Animation timing issues
           - Missing or invalid attributes
           - Version compatibility problems
           - Resource handling errors
        3. Make the minimum changes needed to fix the issue
        4. Preserve the original functionality and intent of the code
        5. Follow Manim best practices in your fixes
        6. Ensure the code remains compatible with ManimCE version 0.17.3
        
        Return ONLY the complete, corrected code without explanations or markdown formatting. The code should be ready to run without any modifications.
        """
        
        self.manim_processor = ManimProcessor()
        
        super().__init__(
            agent=CodeAgent(
                tools=[],
                model=model,
                additional_authorized_imports=["subprocess", "sys", "os"]
            ),
            name="manim_executor",
            description="Executes and debugs Manim code"
        )
    
    def _extract_scene_name(self, code):
        """Extract the Scene class name from the code"""
        import re
        pattern = r"class\s+(\w+Scene)\s*\("
        matches = re.findall(pattern, code)
        return matches[-1] if matches else None
    
    def debug_code(self, code, error):
        """Debug the code using the model"""
        prompt = self.debug_template.format(code=code, error=error)
        response = self.agent.run(prompt)
        return self.manim_processor.extract_code(response)
    
    def execute_code(self, code):
        """Execute the Manim code and return the path to the generated video"""
        with self.manim_processor.create_temp_dir() as temp_dir:
            try:
                scene_name = self._extract_scene_name(code)
                if not scene_name:
                    raise Exception("Could not find a valid Scene class in the code")
                
                scene_file = self.manim_processor.save_code(code, temp_dir)
                video_path = self.manim_processor.render_scene(scene_file, scene_name, temp_dir)
                
                if video_path:
                    import shutil
                    kaggle_output_path = f"/kaggle/working/{scene_name}.mp4"
                    shutil.copy(video_path, kaggle_output_path)
                    print(f"Video saved to {kaggle_output_path}.")
                    return kaggle_output_path
                else:
                    raise Exception("Video file not found after rendering")
            
            except Exception as e:
                print(f"Error during execution: {str(e)}")
                return self.debug_code(code, str(e))

