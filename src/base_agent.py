from typing import Dict, Any
from langchain_groq import ChatGroq
from models import AgentType
import logging

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, llm: ChatGroq, agent_type: AgentType):
        self.name = name
        self.llm = llm
        self.agent_type = agent_type
        logger.info(f"Initialized {self.name} ({agent_type.value})")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Each agent must implement process method")
