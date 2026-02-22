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
        self.lawyer_prompt = load_prompt("legal")
        self.logger = AgentLogger("agent_logs/legal_agent_logs.jsonl")

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        # Full conversation context
        state["last_state"] = "legal"
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get("legal")
        conversation = "\n".join(
            [f"{type(m).__name__}: {m.content}" for m in state["messages"]]
        )

        # Retrieve documents
        context = self.retriever.retrieve(state["query"])
        print("context = ",context)

        full_prompt = self.lawyer_prompt.format(
            context = context,
            chat_history=conversation,
            question=query
        )

        response = await self.llm.ainvoke(full_prompt)

        log_data = {
            "timestamp": self.logger.current_timestamp(),
            "agent": "router",
            "user_query": query,
            "context": context,
            "constructed_prompt": full_prompt,
            "raw_output": response.content,
        }
        self.logger.log(log_data)

        return {
            "messages": [
                AIMessage(content=response.content, name="legal")
            ],
            "agent_outputs":{"legal":response.content} 
        }
