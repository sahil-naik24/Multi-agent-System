from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.base import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.models.state import AgentState


class MergeAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.merge_prompt = load_prompt("merger")

    async def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Merge outputs from specialist agents.
        """
        state["last_state"] = "Merger"
        agent_outputs = state.get("agent_outputs", {})
        print("lenght of agent outputs = ",len(agent_outputs))

        if not agent_outputs:
            return {
                "final_output": "No valid response generated."
            }

        # 🔹 If only one agent responded → bypass LLM
        if len(agent_outputs) == 1:
            single_response = next(iter(agent_outputs.values()))
            return {
                "final_output": single_response
            }

        # 🔹 Multiple agents → synthesize
        combined_content = "\n\n".join(
            f"{agent.upper()} RESPONSE:\n{content}"
            for agent, content in agent_outputs.items()
        )

        full_prompt = self.merge_prompt.format(
            combined_output = combined_content,
            user_query=state["query"]
        )

        response = await self.llm.ainvoke(full_prompt)

        return {
            "final_output": response.content
        }
