from langchain.prompts import ChatPromptTemplate
from base_agent import BaseAgent
from models import AgentType

class NarratorAgent(BaseAgent):
    """Agent responsible for creating narration scripts"""
    
    def __init__(self, llm: ChatGroq):
        super().__init__("Narrator", llm, AgentType.NARRATOR)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data['request']
        scene_outline = input_data.get('scene_outline', '')
        
        logger.info(f"Generating narration script for: {request.description}")
        
        script_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional educational content narrator. Create engaging, clear narration scripts."),
            ("human", f"""
            Create a narration script for a {request.duration}-second animation about: {request.description}
            
            Requirements:
            1. Clear, engaging narration matching visual elements
            2. Should be exactly {request.duration} seconds when spoken
            3. Educational and informative tone
            4. Natural speech patterns
            
            Scene Outline:
            {scene_outline}
            
            Write only the script text, no formatting.
            """)
        ])
        
        chain = script_prompt | self.llm
        response = chain.invoke({})
        
        return {
            "script": response.content.strip()
        }
