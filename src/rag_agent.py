from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from base_agent import BaseAgent
from models import AgentType

class RAGRouterAgent(BaseAgent):
    """Agent responsible for RAG system and context retrieval"""
    
    def __init__(self, llm: ChatGroq):
        super().__init__("RAG Router", llm, AgentType.RAG_ROUTER)
        self.setup_embeddings()
        self.setup_rag_system()
    
    def setup_embeddings(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
    def setup_rag_system(self):
        docs_content = [
            "Manim Scene: A Scene is the main container for animations. Use Scene class to create animations.",
            "Manim Mobject: Mathematical objects (Mobject) are the building blocks of Manim animations.",
            "Manim Animations: Use Create(), Write(), Transform(), FadeIn(), FadeOut() for basic animations.",
            "Manim Camera: Control camera with self.camera.frame to zoom, pan, and rotate views.",
            "Manim Text: Use Text(), MathTex(), Tex() for displaying text and mathematical expressions.",
            "Manim Shapes: Circle(), Square(), Rectangle(), Line() for basic geometric shapes.",
            "Manim Colors: Use Color palette like BLUE, RED, GREEN, YELLOW for coloring objects.",
            "Manim Positioning: Use .move_to(), .shift(), .next_to() for positioning objects.",
            "Manim Grouping: Use Group() to group multiple objects together.",
            "Manim Timing: Use self.play() with run_time parameter to control animation timing.",
            "Manim Indentation: Always use 4 spaces for indentation, never tabs.",
            "Manim Imports: Use 'from manim import *' for all Manim objects and animations.",
            "Manim Variables: Initialize all variables before using them in animations."
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        docs = text_splitter.create_documents(docs_content)
        
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get('query', '')
        relevant_docs = self.retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        return {
            "context": context,
            "relevant_documents": relevant_docs
        }
