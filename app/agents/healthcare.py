from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.agents.base import BaseAgent
from app.tools.tool_registry import shared_tool_list
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState
from langchain_core.prompts import ChatPromptTemplate

class HealthcareAgent(BaseAgent):

    def __init__(self):
        super().__init__()

        self.healthcare_prompt = load_prompt("healthcare")
        self.tools = shared_tool_list
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.prompt = self._build_prompt()

    def _build_prompt(self):

        return ChatPromptTemplate.from_messages(
            [
                ("system", self.healthcare_prompt),
                ("human", "{input}")            ]
        )

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Healthcare domain agent.
        """
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get("healthcare")

        if not query:
            return {}

        messages = state.get("messages_healthcare")

        if not messages:
            messages = self.prompt.format_messages(input=query)

        response = await self.llm_with_tools.ainvoke(messages)

        if isinstance(response, AIMessage) and response.tool_calls:
            for call in response.tool_calls:
                print(f"[HealthcareAgent] Tool selected,'tool_name': {call['name']}")

        # Always return the message
        result = {
            "messages_healthcare": messages + [response]
        }

        # ONLY finalize output if NO tool call
        if isinstance(response, AIMessage) and not response.tool_calls:
            result["agent_outputs"] = {
                "healthcare": response.content
            }

        return result
