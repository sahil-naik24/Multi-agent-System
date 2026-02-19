from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.base import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState


class SoftwareAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.system_prompt = load_prompt("software")

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Software domain agent.
        Uses internal LLM knowledge only.
        """

        # Get sub-query from router
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get("software")

        if not query:
            return {}

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=query),
        ]

        response = await self.llm.ainvoke(messages)

        # Create named AI message
        ai_message = AIMessage(
            content=response.content,
            name="software"
        )

        return {
            # Append to conversation safely
            "messages": [ai_message],

            # Parallel-safe structured output
            "agent_outputs":
                {"software" : response.content}
        }
