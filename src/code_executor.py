import subprocess
import os
import sys
import shutil
from base_agent import BaseAgent
from code_generator import CodeGeneratorAgent
from models import AgentType, IterationResult
from utils import create_temp_dir, extract_scene_name

class CodeExecutorAgent(BaseAgent):
    """Agent responsible for executing and debugging Manim code"""
    
    def __init__(self, llm: ChatGroq, code_generator: CodeGeneratorAgent, output_dir: str):
        super().__init__("Code Executor", llm, AgentType.CODE_EXECUTOR)
        self.code_generator = code_generator
        self.output_dir = output_dir
        self.max_iterations = 5
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Manim code with iterative debugging"""
        code = input_data['code']
        
        logger.info(f"🎬 Executing Manim code")
        
        # First attempt
        initial_result = self._execute_code_once(code)
        
        if initial_result['success']:
            return initial_result
        
        # If failed, try iterative debugging
        logger.info("🔧 Initial execution failed, starting iterative debugging...")
        debug_result = self.debug_code_iteratively(code, initial_result['error'])
        
        if debug_result.success:
            logger.info("✅ Code fixed through iterative debugging")
            return self._execute_code_once(debug_result.code)
        else:
            logger.error("❌ Could not fix code through iterative debugging")
            return {
                "success": False,
                "error": f"Code could not be fixed after {self.max_iterations} iterations. Last error: {debug_result.error}",
                "debug_attempts": debug_result.iteration
            }
    
    def debug_code_iteratively(self, initial_code: str, initial_error: str) -> IterationResult:
        """Debug code with iterative learning approach"""
        attempts = []
        current_code = initial_code
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"🔄 Debug iteration {iteration}/{self.max_iterations}")
            
            # Test current code
            execution_result = self.test_code_execution(current_code)
            
            if execution_result['success']:
                logger.info(f"✅ Code fixed successfully in iteration {iteration}")
                return IterationResult(
                    iteration=iteration,
                    code=current_code,
                    success=True
                )
            
            error_message = execution_result['error']
            error_type = self.code_generator.identify_error_type(error_message)
            
            # Record this attempt
            attempt = IterationResult(
                iteration=iteration,
                code=current_code,
                error=error_message,
                error_type=error_type
            )
            attempts.append(attempt)
            
            # Use code generator to debug
            try:
                new_code = self.code_generator.debug_code(current_code, error_message, attempts[:-1])
                if new_code and new_code != current_code:
                    current_code = new_code
                    logger.info(f"🔧 Applied debugging fixes for {error_type} error")
                else:
                    logger.warning(f"⚠️ No different solution provided in iteration {iteration}")
                    if iteration > 2:
                        break
                        
            except Exception as e:
                logger.error(f"❌ Error in debugging iteration {iteration}: {e}")
                break
        
        logger.warning(f"⚠️ Could not fix code after {self.max_iterations} iterations")
        return IterationResult(
            iteration=self.max_iterations,
            code=current_code,
            error=f"Could not fix after {self.max_iterations} attempts",
            success=False
        )
    
    def test_code_execution(self, code: str) -> Dict[str, Any]:
        """Test code execution without creating video file"""
        with self._create_temp_dir() as temp_dir:
            try:
                scene_name = self._extract_scene_name(code)
                if not scene_name:
                    return {
                        "success": False,
                        "error": "Could not find a valid Scene class in the code"
                    }
                
                script_path = os.path.join(temp_dir, "test_scene.py")
                with open(script_path, "w") as f:
                    f.write(code)
                
                # Test syntax by importing the module
                sys.path.insert(0, temp_dir)
                
                try:
                    spec = importlib.util.spec_from_file_location("test_scene", script_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if the scene class exists and is properly defined
                    if hasattr(module, scene_name):
                        scene_class = getattr(module, scene_name)
                        if hasattr(scene_class, 'construct'):
                            return {"success": True}
                        else:
                            return {"success": False, "error": f"Scene class {scene_name} missing construct method"}
                    else:
                        return {"success": False, "error": f"Scene class {scene_name} not found"}
                        
                except Exception as e:
                    return {"success": False, "error": str(e)}
                finally:
                    sys.path.remove(temp_dir)
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def _execute_code_once(self, code: str) -> Dict[str, Any]:
        """Execute the Manim code once and return the path to the generated video"""
        with self._create_temp_dir() as temp_dir:
            try:
                scene_name = self._extract_scene_name(code)
                if not scene_name:
                    raise Exception("Could not find a valid Scene class in the code")
                
                script_path = os.path.join(temp_dir, "scene.py")
                with open(script_path, "w") as f:
                    f.write(code)
                
                logger.info(f"Executing scene: {scene_name}")
                
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
                    return {
                        "success": False,
                        "error": result.stderr,
                        "stdout": result.stdout,
                        "scene_name": scene_name
                    }
                
                # Find and copy the generated video
                video_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.mp4'):
                            video_files.append(os.path.join(root, file))
                
                if not video_files:
                    return {
                        "success": False,
                        "error": f"No video files generated",
                        "scene_name": scene_name
                    }
                
                # Copy to output directory
                video_path = video_files[0]
                output_filename = f"output_{scene_name}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                shutil.copy(video_path, output_path)
                
                return {
                    "success": True,
                    "video_path": output_path,
                    "scene_name": scene_name,
                    "stdout": result.stdout
                }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "scene_name": scene_name if 'scene_name' in locals() else None
                }
    
    @contextmanager
    def _create_temp_dir(self):
        """Create a temporary directory context manager"""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_scene_name(self, code: str) -> Optional[str]:
        """Extract the scene class name from the code"""
        # Look for class definitions that inherit from Scene
        pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*Scene[^)]*\):'
        matches = re.findall(pattern, code)
        if matches:
            return matches[0]
        
        # Fallback: look for any class with Scene in the name
        pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*Scene[A-Za-z0-9_]*)\s*\([^)]*\):'
        matches = re.findall(pattern, code)
        if matches:
            return matches[0]
        
        return None