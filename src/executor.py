from smolagents import HfApiModel, CodeAgent, ManagedAgent
import subprocess
import tempfile
import os
from pathlib import Path
import shutil
import sys
from contextlib import contextmanager
import re
# from utils.utils import *

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
        
        super().__init__(
            agent=CodeAgent(
                tools=[],
                model=model,
                additional_authorized_imports=["subprocess", "sys", "os"]
            ),
            name="manim_executor",
            description="Executes and debugs Manim code"
        )
    
    @contextmanager
    def _create_temp_dir(self):
        """Context manager for creating and cleaning up temporary directory"""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
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
        return extract_code(response)  
    
    def execute_code(self, code):
        """Execute the Manim code and return the path to the generated video"""
        with self._create_temp_dir() as temp_dir:
            try:
                scene_name = self._extract_scene_name(code)
                if not scene_name:
                    raise Exception("Could not find a valid Scene class in the code")
                
                script_path = os.path.join(temp_dir, "scene.py")
                with open(script_path, "w") as f:
                    f.write(code)
                
                result = subprocess.run(
                    [
                        "python",
                        "-m",
                        "manim",
                        "-ql",
                        "--media_dir", temp_dir,
                        script_path,
                        scene_name
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )
                
                if result.returncode != 0:
                    fixed_code = self.debug_code(code, result.stderr)
                    return self.execute_code(fixed_code)
                
                videos_dir = os.path.join(temp_dir, "videos", "scene", "480p15")
                if not os.path.exists(videos_dir):
                    raise Exception(f"Videos directory not found: {videos_dir}")
                    
                video_path = os.path.join(videos_dir, f"{scene_name}.mp4")
                if not os.path.exists(video_path):
                    raise Exception(f"Video file not found: {video_path}")
                
                current_dir = os.getcwd()
                output_path = os.path.join(current_dir, f"output_{scene_name}.mp4")
                
                print(f"Copying from {video_path} to {output_path}")
                shutil.copy(video_path, output_path)
                
                if os.path.exists(output_path):
                    print(f"Successfully saved video to {output_path}")
                    return output_path
                else:
                    raise Exception(f"Failed to save video to {output_path}")
                    
            except Exception as e:
                print(f"Error during execution: {str(e)}")
                if isinstance(e, subprocess.CalledProcessError):
                    return self.debug_code(code, e.stderr)
                return self.debug_code(code, str(e))
