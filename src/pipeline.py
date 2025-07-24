from langchain_groq import ChatGroq
from manager import ManagerAgent
from models import AnimationRequest
from utils import ensure_directory_exists
import os
import logging

class AnimationPipeline:
    """Main pipeline class for the multi-agent animation system"""
    
    def __init__(self, groq_api_key: str, sarvam_api_key: str = None, output_dir: str = "/kaggle/working"):
        """Initialize the animation pipeline"""
        self.groq_api_key = groq_api_key
        self.sarvam_api_key = sarvam_api_key
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-70b-8192",
            temperature=0.1
        )
        
        # Initialize the manager agent
        self.manager = ManagerAgent(self.llm, sarvam_api_key, output_dir)
        
        logger.info("🚀 Animation Pipeline initialized successfully")
    
    def create_animation(self, description: str, duration: int = 10, style: str = "educational", complexity: str = "medium") -> Dict[str, Any]:
        """Create an animation based on the given parameters"""
        request = AnimationRequest(
            description=description,
            duration=duration,
            style=style,
            complexity=complexity
        )
        
        logger.info(f"🎬 Creating animation: {description}")
        
        # Process the request through the manager
        results = self.manager.process({'request': request})
        
        return results
    
    def get_available_outputs(self) -> List[str]:
        """Get list of available output files"""
        outputs = []
        for file in os.listdir(self.output_dir):
            if file.endswith(('.mp4', '.wav', '.py')):
                outputs.append(os.path.join(self.output_dir, file))
        return outputs