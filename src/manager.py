from base_agent import BaseAgent
from rag_agent import RAGRouterAgent
from planner import PlannerAgent
from code_generator import CodeGeneratorAgent
from code_executor import CodeExecutorAgent
from narrator import NarratorAgent
from audio_generator import AudioGeneratorAgent
from models import AgentType

class ManagerAgent(BaseAgent):
    """Manager agent that coordinates all other agents"""
    
    def __init__(self, llm: ChatGroq, sarvam_api_key: str = None, output_dir: str = "/kaggle/working"):
        super().__init__("Manager", llm, AgentType.MANAGER)
        self.output_dir = output_dir
        
        # Initialize all agents
        self.rag_agent = RAGRouterAgent(llm)
        self.planner_agent = PlannerAgent(llm, self.rag_agent)
        self.code_generator_agent = CodeGeneratorAgent(llm, self.rag_agent)
        self.code_executor_agent = CodeExecutorAgent(llm, self.code_generator_agent, output_dir)
        self.narrator_agent = NarratorAgent(llm)
        self.audio_generator_agent = AudioGeneratorAgent(llm, sarvam_api_key)
        
        logger.info("Manager Agent initialized with all sub-agents")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data['request']
        
        logger.info(f"Starting animation generation for: {request.description}")
        
        results = {}
        
        try:
            # Step 1: Create scene outline
            print("\n" + "="*60)
            print("STEP 1: CREATING SCENE OUTLINE")
            print("="*60)
            
            planner_result = self.planner_agent.process({'request': request})
            results["scene_outline"] = planner_result["scene_outline"]
            
            print("SCENE OUTLINE:")
            print("-" * 40)
            print(planner_result["scene_outline"])
            
            # Step 2: Generate Manim code
            print("\n" + "="*60)
            print("STEP 2: GENERATING MANIM CODE")
            print("="*60)
            
            code_gen_result = self.code_generator_agent.process({
                'request': request,
                'scene_outline': planner_result["scene_outline"]
            })
            results["code"] = code_gen_result["code"]
            
            print("GENERATED MANIM CODE:")
            print("-" * 40)
            print(code_gen_result["code"])
            
            # Step 3: Execute Manim code
            print("\n" + "="*60)
            print("STEP 3: EXECUTING MANIM CODE")
            print("="*60)
            
            execution_result = self.code_executor_agent.process({
                'code': code_gen_result["code"]
            })
            results["execution_result"] = execution_result
            
            print("EXECUTION RESULTS:")
            print("-" * 40)
            print(f"Success: {execution_result.get('success', False)}")
            
            if execution_result.get('success'):
                print(f"Video Path: {execution_result.get('video_path')}")
                print(f"Scene Name: {execution_result.get('scene_name')}")
            else:
                print(f"Error: {execution_result.get('error', 'Unknown error')}")
                if 'debug_attempts' in execution_result:
                    print(f"Debug attempts made: {execution_result['debug_attempts']}")
            
            # Step 4: Generate narration script
            print("\n" + "="*60)
            print("STEP 4: GENERATING NARRATION SCRIPT")
            print("="*60)
            
            narrator_result = self.narrator_agent.process({
                'request': request,
                'scene_outline': planner_result["scene_outline"]
            })
            results["narration"] = narrator_result["script"]
            
            print("NARRATION SCRIPT:")
            print("-" * 40)
            print(narrator_result["script"])
            
            # Step 5: Generate audio (if TTS is available)
            print("\n" + "="*60)
            print("STEP 5: GENERATING AUDIO NARRATION")
            print("="*60)
            
            if SARVAM_AVAILABLE and self.audio_generator_agent.sarvam_api_key:
                audio_result = self.audio_generator_agent.process({
                    'script': narrator_result["script"],
                    'output_dir': self.output_dir
                })
                results["audio_result"] = audio_result
                
                print("AUDIO GENERATION RESULTS:")
                print("-" * 40)
                print(f"Success: {audio_result.get('success', False)}")
                
                if audio_result.get('success'):
                    print(f"Audio File: {audio_result.get('audio_file')}")
                    
                    # Step 6: Combine audio and video
                    if execution_result.get('success'):
                        print("\n" + "="*60)
                        print("STEP 6: COMBINING AUDIO AND VIDEO")
                        print("="*60)
                        
                        combine_result = self.audio_generator_agent.combine_audio_video(
                            execution_result["video_path"],
                            audio_result["audio_file"],
                            self.output_dir
                        )
                        results["final_video"] = combine_result
                        
                        print("FINAL VIDEO RESULTS:")
                        print("-" * 40)
                        print(f"Success: {combine_result.get('success', False)}")
                        if combine_result.get('success'):
                            print(f"Final Video: {combine_result.get('final_video')}")
                        else:
                            print(f"Error: {combine_result.get('error')}")
                else:
                    print(f"Audio Error: {audio_result.get('error')}")
            else:
                print("Audio generation skipped - TTS not available or API key not provided")
                results["audio_result"] = {"success": False, "error": "TTS not available"}
            
            # Final summary
            print("\n" + "="*60)
            print("FINAL SUMMARY")
            print("="*60)
            
            summary = {
                "animation_request": request.description,
                "duration": request.duration,
                "style": request.style,
                "scene_planning": "✅ Completed",
                "code_generation": "✅ Completed",
                "code_execution": "✅ Success" if execution_result.get('success') else "❌ Failed",
                "narration": "✅ Completed",
                "audio_generation": "✅ Success" if results.get("audio_result", {}).get('success') else "❌ Failed/Skipped",
                "final_video": "✅ Success" if results.get("final_video", {}).get('success') else "❌ Failed/Skipped"
            }
            
            for key, value in summary.items():
                if key == "animation_request":
                    print(f"{key.replace('_', ' ').title()}: {value}")
                elif key in ["duration", "style"]:
                    print(f"{key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
            
            results["summary"] = summary
            return results
            
        except Exception as e:
            logger.error(f"Error in animation generation pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": results
            }
