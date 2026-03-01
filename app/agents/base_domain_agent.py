from langchain_core.messages import HumanMessage
from app.agents.registry import TOOL_REGISTRY, AGENT_PERMISSIONS
from app.models.state import AgentState
from app.agents.base import BaseAgent
from app.utils.prompt_loader import load_prompt
from langchain.agents import create_agent 
from langchain_core.callbacks import BaseCallbackHandler

class ToolExecutionPrinter(BaseCallbackHandler):
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name")
        print(f"\n[EXECUTING TOOL]: {tool_name}")
        print(f"[INPUT]: {input_str}\n")

class BaseDomainAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__()
        self.agent_id = agent_id
        self.raw_prompt_string = load_prompt(self.agent_id)
        self.system_prompt = self._build_prompt()
        self.agent_executor = self._build_agent()

    def _build_prompt(self):
        return self.raw_prompt_string

    def _build_agent(self):
        allowed_names = AGENT_PERMISSIONS.get(self.agent_id, [])
        tools = [TOOL_REGISTRY[name] for name in allowed_names if name in TOOL_REGISTRY]
        
        # Note: state_modifier is where the system prompt goes
        return create_agent(self.llm, tools=tools, system_prompt=self.system_prompt)

    async def invoke(self, state: AgentState):
        sub_queries = state.get("sub_queries", {})
        query = sub_queries.get(self.agent_id)
        
        if not query: 
            return {}

        workspace = state.get("agent_workspace", {})
        history = workspace.get(self.agent_id, [])

        # Use history if it exists, otherwise start fresh with the sub-query
        input_messages = history if history else [HumanMessage(content=query)]
        
        # Use the corrected name: self.agent_executor
        result = await self.agent_executor.ainvoke(
            {"messages": input_messages},
            config={"callbacks": [ToolExecutionPrinter()]}  # ← verbose equivalent
        )
        
        return {
            "agent_workspace": {self.agent_id: result["messages"]},
            "agent_outputs": {self.agent_id: result["messages"][-1].content}
        }