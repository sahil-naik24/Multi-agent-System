# Base Agent Interface
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.llm.get_llm_model import get_chat_model
from app.models.state import AgentState

load_dotenv()

class BaseAgent(ABC):
    def __init__(self):
        # Initialize the LLM once for all agents
        self.llm = get_chat_model()

    @abstractmethod
    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the state and return a dictionary of updates.
        """
        pass