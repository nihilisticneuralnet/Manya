import os
import shutil
import subprocess
import tempfile
from manim import *

class ManimExecutorAgent:
    """Agent responsible for executing and debugging Manim code without model."""
    
    def __init__(self):
        pass  

    def _create_temp_dir(self):
        """Creates and cleans up a temporary directory."""
        temp_dir = tempfile.mkdtemp()
        return temp_dir

    def _extract_scene_name(self, code):
        """Extracts the Scene class name from the code."""
        import re
        pattern = r"class\s+(\w+Scene)\s*\("
        matches = re.findall(pattern, code)
        return matches[-1] if matches else None

    def execute_code(self, code):
        """Executes the Manim code and returns the path to the generated video."""
        temp_dir = self._create_temp_dir()
        try:
            scene_name = self._extract_scene_name(code)
            if not scene_name:
                raise Exception("Could not find a valid Scene class in the code")
            
            script_path = os.path.join(temp_dir, "scene.py")
            with open(script_path, "w") as f:
                f.write(code)

            result = subprocess.run(
                ["python", "-m", "manim", "-ql", "--media_dir", temp_dir, script_path, scene_name],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None

            videos_dir = os.path.join(temp_dir, "videos", "scene", "480p15")
            video_path = os.path.join(videos_dir, f"{scene_name}.mp4")

            if not os.path.exists(video_path):
                raise Exception("Video file not found.")

            output_path = os.path.join(os.getcwd(), f"output_{scene_name}.mp4")
            shutil.copy(video_path, output_path)

            return output_path if os.path.exists(output_path) else None
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_code = """  
from manim import *  

class TestScene(Scene):  
    def construct(self):  
        text = Text("Hello, Manim!")  
        self.play(Write(text))  
        self.wait(2)  
"""

    agent = ManimExecutorAgent()
    output_video = agent.execute_code(test_code)

    if output_video:
        print(f"Video generated successfully: {output_video}")
    else:
        print("Failed to generate video.")
