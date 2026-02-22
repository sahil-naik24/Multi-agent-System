from typing import Dict, Any
from langchain_core.messages import AIMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor #change later
from app.agents.base import BaseAgent
from app.tools.search import medical_search
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState
from langchain_core.prompts import ChatPromptTemplate


class HealthcareAgent(BaseAgent):

    def __init__(self):
        super().__init__()

        self.healthcare_prompt = load_prompt("healthcare")
        self.tools = [medical_search]
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            prompt=self._build_prompt()
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False
        )

    def _build_prompt(self):

        return ChatPromptTemplate.from_messages(
            [
                ("system", self.healthcare_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        )

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Healthcare domain agent.
        """
        state["last_state"] = "healthcare"
        print("Enter ")
        # Use sub-query from router
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get("healthcare")

        if not query:
            return {}

        # Async tool agent execution
        result = await self.executor.ainvoke({"input": query})

        output_text = result["output"]

        return {
            "messages": [
                AIMessage(content=output_text, name="healthcare")
            ],
            "agent_outputs": {"healthcare":output_text}
        }
