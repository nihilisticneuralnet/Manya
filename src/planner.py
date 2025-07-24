from langchain.prompts import ChatPromptTemplate
from base_agent import BaseAgent
from rag_agent import RAGRouterAgent
from models import AgentType

class PlannerAgent(BaseAgent):
    """Agent responsible for creating scene outlines and storyboards"""
    
    def __init__(self, llm: ChatGroq, rag_agent: RAGRouterAgent):
        super().__init__("Scene Planner", llm, AgentType.PLANNER)
        self.rag_agent = rag_agent
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed scene outline"""
        request = input_data['request']
        
        logger.info(f"🎬 Creating scene outline for: {request.description}")
        
        # Get relevant context
        rag_result = self.rag_agent.process({'query': request.description})
        context = rag_result['context']
        
        scene_prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an expert animation director. Create detailed scene outlines for educational {request.style} animations."),
            ("human", f"""
            Create a detailed scene outline for a {request.duration}-second Manim animation about: {request.description}
            
            Break it down into:
            1. Scene progression (what happens when)
            2. Key visual elements needed
            3. Timing for each scene (in seconds)
            4. Transitions between scenes
            5. Make sure the text doesn't overlap 
            
            Style: {request.style}
            Complexity: {request.complexity}
            
            Relevant Manim concepts:
            {context}
            
            Provide a clear, structured outline with specific timings.
            """)
        ])
        
        chain = scene_prompt | self.llm
        response = chain.invoke({})
        
        return {
            "scene_outline": response.content,
            "context": context
        }