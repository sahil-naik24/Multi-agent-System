# Base Agent Interface
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI
import app.core.config as CONFIG
from app.models.state import AgentState

load_dotenv()

class BaseAgent(ABC):
    def __init__(self):
        # Initialize the LLM once for all agents
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CM_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CM_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CM_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_CM_DEPLOYMENT_NAME"),
            temperature=os.getenv("MODEL_TEMPERATURE")
        )

    @abstractmethod
    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Process the state and return a dictionary of updates.
        """
        pass