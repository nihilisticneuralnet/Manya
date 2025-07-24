import subprocess
import os
from base_agent import BaseAgent
from models import AgentType

# Try to import Sarvam AI (optional)
try:
    from sarvam.client import SarvamAI
    from sarvam.utils import save
    SARVAM_AVAILABLE = True
except ImportError:
    SARVAM_AVAILABLE = False

class AudioGeneratorAgent(BaseAgent):
    """Agent responsible for generating audio narration"""
    
    def __init__(self, llm: ChatGroq, sarvam_api_key: str = None):
        super().__init__("Audio Generator", llm, AgentType.AUDIO_GENERATOR)
        self.sarvam_api_key = sarvam_api_key
        self.setup_tts()
    
    def setup_tts(self):
        """Initialize TTS client"""
        try:
            if SARVAM_AVAILABLE and self.sarvam_api_key:
                self.tts_client = SarvamAI(api_subscription_key=self.sarvam_api_key)
                logger.info("✅ TTS client initialized successfully")
            else:
                self.tts_client = None
                logger.warning("⚠️ TTS not available - API key missing or Sarvam not installed")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTS: {e}")
            self.tts_client = None
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio narration from script"""
        script = input_data['script']
        output_dir = input_data['output_dir']
        
        logger.info(f"🔊 Generating audio narration")
        
        try:
            if not self.tts_client:
                return {
                    "success": False,
                    "error": "TTS client not available"
                }
            
            output_file = os.path.join(output_dir, "narration.wav")
            audio = self.tts_client.text_to_speech.convert(
                target_language_code="en-IN",
                text=script,
                model="bulbul:v2",
                speaker="anushka"
            )
            save(audio, output_file)
            
            return {
                "success": True,
                "audio_file": output_file
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def combine_audio_video(self, video_file: str, audio_file: str, output_dir: str) -> Dict[str, Any]:
        """Combine video and audio into final animation"""
        try:
            output_file = os.path.join(output_dir, "final_animation.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "final_video": output_file
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }