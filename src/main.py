import os
import logging
from typing import Dict, Any, List

from pipeline import AnimationPipeline
from models import AnimationRequest
from utils import setup_logging, ensure_directory_exists

logger = setup_logging()

def main():
    """Main entry point for the animation system"""
    print("🎬 Multi-Agent Manim Animation System")
    print("=" * 50)
    print("- RAG Router: Provides relevant Manim documentation context")
    print("- Planner: Creates scene outlines and storyboards")
    print("- Code Generator: Generates and debugs Manim Python code")
    print("- Code Executor: Executes code with iterative error fixing")
    print("- Narrator: Creates narration scripts")
    print("- Audio Generator: Converts text to speech and combines with video")
    print("- Manager: Coordinates all agents and manages the pipeline")
    
    # Get API keys from environment
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "sk_ys5zk0cw_fz7vUES7shW6SU0QKQdX2Bv6")
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not found in environment variables")
        return
    
    # Setup output directory
    output_dir = "./output"
    ensure_directory_exists(output_dir)
    
    # Initialize pipeline
    try:
        pipeline = AnimationPipeline(
            groq_api_key=GROQ_API_KEY,
            sarvam_api_key=SARVAM_API_KEY,
            output_dir=output_dir
        )
        
        # Example animation creation
        print("\n🚀 Creating example animation...")
        results = pipeline.create_animation(
            description="Expand (a+b)^2. Don't draw any square",
            duration=15,
            style="educational",
            complexity="medium"
        )
        
        print("\n🎉 ANIMATION CREATION COMPLETED")
        print("=" * 50)
        
        # Display results
        if "summary" in results:
            summary = results["summary"]
            for key, value in summary.items():
                if key == "animation_request":
                    print(f"📝 {key.replace('_', ' ').title()}: {value}")
                elif key in ["duration", "style"]:
                    print(f"⚙️ {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # List available outputs
        outputs = pipeline.get_available_outputs()
        if outputs:
            print(f"\n📁 Available output files:")
            for output in outputs:
                print(f"   - {output}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline initialization failed: {e}")
        return {"success": False, "error": str(e)}

def create_custom_animation(description: str, duration: int = 10, 
                           style: str = "educational", complexity: str = "medium",
                           output_dir: str = "./output") -> Dict[str, Any]:
    """
    Create a custom animation with provided parameters
    
    Args:
        description: Natural language description of the animation
        duration: Duration in seconds
        style: Animation style (educational, presentation, etc.)
        complexity: Complexity level (simple, medium, complex)
        output_dir: Output directory for generated files
    
    Returns:
        Dictionary containing results and status
    """
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not found in environment variables")
        return {"success": False, "error": "Missing GROQ_API_KEY"}
    
    try:
        ensure_directory_exists(output_dir)
        
        pipeline = AnimationPipeline(
            groq_api_key=GROQ_API_KEY,
            sarvam_api_key=SARVAM_API_KEY,
            output_dir=output_dir
        )
        
        results = pipeline.create_animation(
            description=description,
            duration=duration,
            style=style,
            complexity=complexity
        )
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Custom animation creation failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Set up environment variables if not already set
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ Warning: Set GROQ_API_KEY environment variable")
        print("   Example: export GROQ_API_KEY='your_key_here'")
    
    if not os.getenv("SARVAM_API_KEY"):
        print("⚠️ Optional: Set SARVAM_API_KEY for audio generation")
        print("   Example: export SARVAM_API_KEY='your_key_here'")
    
    # Run the main application
    main()
