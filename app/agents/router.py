"""
Parent Router Agent
Responsible for:
- Intent classification
- Multi-domain detection
- Query splitting
- Injection filtering
"""

import json
import re
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.base import BaseAgent
from app.utils.prompt_loader import load_prompt
import app.core.config as CONFIG 
from app.utils.agent_logger import AgentLogger

class ParentAgent(BaseAgent):
    """
    Intelligent Router Agent
    """

    def __init__(self):
        super().__init__()
        self.router_prompt = load_prompt("router")
        self.logger = AgentLogger("agent_logs/router_logs.jsonl")

    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
            Parent agent for routing
        """
        state["last_state"] = "router"
        
        # Get latest user message
        if not state.get("messages"):
            raise ValueError("No messages found in state.")

        last_message = state["messages"][-1]
        if not isinstance(last_message, HumanMessage):
            return {}

        user_query = state["query"]

        # Guardrail: basic injection detection
        if self._is_malicious(user_query):
            return {
                "next_steps": [],
                "messages": [AIMessage(content="Query rejected due to unsafe instructions.", name="router")]
            }
        
        agents_description = "\n".join(f'{k}: {v}' for k,v in CONFIG.AVAILABLE_AGENTS.items())

        # Build prompt
        full_prompt = self.router_prompt.format(
            available_agents=agents_description,
            chat_history=state["messages"],
            question=user_query
)
        response = await self.llm.ainvoke(full_prompt)

        parsed = self._safe_parse(response.content)

        log_data = {
            "timestamp": self.logger.current_timestamp(),
            "agent": "router",
            "user_query": user_query,
            "parsed_output": parsed,
            "constructed_prompt": full_prompt,
            
        }
        self.logger.log(log_data)


        # If invalid
        if not parsed or not parsed.get("valid"):
            invalid_message = "Query provided is outside domain or not valid.Please clarify"
            return {
                "final_output": invalid_message,
                "next_steps": [],
                "messages": [
                    AIMessage(
                        content=invalid_message,
                        name="router"
                    )
                ]
            }

        domains = parsed.get("domains", [])
        sub_queries = parsed.get("sub_queries", {})

        return {
            "next_steps": domains,
            "sub_queries": sub_queries,
            "agent_outputs": None,
            "messages": [
                AIMessage(
                    content=f"Routing to: {', '.join(domains)}",
                    name="router"
                )
            ]
        }

    # --------------------------------------------------
    # Helper: Safe JSON Parsing
    # --------------------------------------------------

    def _safe_parse(self, text: str) -> Dict[str, Any]:
        """Parse JSON safely, strip markdown if present"""
        try:
            text = text.strip().strip("```json").strip("```")
            return json.loads(text)
        except Exception:
            return {}

    # --------------------------------------------------
    # Helper: Basic Injection Guard
    # --------------------------------------------------

    def _is_malicious(self, query: str) -> bool:
        """Detect common prompt injection attempts"""
        forbidden_patterns = [
            r"ignore\s+previous\s+instructions",
            r"override\s+system\s+prompt",
            r"act\s+as",
            r"bypass",
            r"developer\s+mode"
        ]
        query_lower = query.lower()
        return any(re.search(p, query_lower) for p in forbidden_patterns)
