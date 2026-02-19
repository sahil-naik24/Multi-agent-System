# Software Agent Logic

from typing import Dict, Any
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from app.agents.base import BaseAgent
from app.tools.rag import LegalRetriever
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState
from app.utils.agent_logger import AgentLogger

class LawyerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.retriever = LegalRetriever()
        self.system_prompt = load_prompt("legal")
        self.logger = AgentLogger("agent_logs/legal_agent_logs.jsonl")

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        # Full conversation context
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get("healthcare")
        conversation = "\n".join(
            [f"{type(m).__name__}: {m.content}" for m in state["messages"]]
        )

        # Retrieve documents
        context = self.retriever.retrieve(state["query"])
        print("context = ",context)

        full_prompt = self.router_prompt.format(
            context = context,
            chat_history=state["messages"],
            question=query
)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=full_prompt)
        ]

        response = await self.llm.ainvoke(messages)

        log_data = {
            "timestamp": self.logger.current_timestamp(),
            "agent": "router",
            "user_query": user_query,
            "context": context,
            "constructed_prompt": augmented_prompt,
            "raw_output": response.content,
        }
        self.logger.log(log_data)

        return {
            # Append to conversation safely
            "messages": [
                AIMessage(content=response.content, name="legal")
            ],
            "agent_outputs":{"legal":response.content} 
        }
