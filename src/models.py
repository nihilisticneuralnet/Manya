from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

@dataclass
class AnimationRequest:
    """Structure for animation requests"""
    description: str
    duration: int  # in seconds
    style: str = "educational"
    complexity: str = "medium"
    
@dataclass
class SceneOutline:
    """Structure for scene planning"""
    scenes: List[Dict[str, Any]]
    timeline: Dict[str, float]
    visual_elements: List[str]
    transitions: List[str]

@dataclass
class StoryboardPlan:
    """Structure for storyboard planning"""
    keyframes: List[Dict[str, Any]]
    visual_flow: List[str]
    camera_movements: List[str]

@dataclass
class TechnicalPlan:
    """Structure for technical implementation"""
    manim_objects: List[str]
    animations: List[str]
    code_structure: Dict[str, Any]
    dependencies: List[str]

@dataclass
class NarrationPlan:
    """Structure for narration planning"""
    script: str
    timing: Dict[str, float]
    voice_settings: Dict[str, Any]

@dataclass
class IterationResult:
    """Store results from each iteration attempt"""
    iteration: int
    code: str
    error: Optional[str] = None
    success: bool = False
    error_type: Optional[str] = None
    fixes_applied: List[str] = None

class AgentType(Enum):
    MANAGER = "manager"
    PLANNER = "planner"
    CODE_GENERATOR = "code_generator"
    CODE_EXECUTOR = "code_executor"
    NARRATOR = "narrator"
    AUDIO_GENERATOR = "audio_generator"
    RAG_ROUTER = "rag_router"