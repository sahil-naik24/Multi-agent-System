from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.base_domain_agent import BaseDomainAgent
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState
from app.tools.tool_registry import shared_tool_list
from app.utils.agent_logger import AgentLogger
from langchain_core.prompts import ChatPromptTemplate

# Specialized Domain Agents
class SoftwareAgent(BaseDomainAgent):
    def __init__(self):
        super().__init__("software")