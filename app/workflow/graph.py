"""
LangGraph Construction for Multi-Agent system
"""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.models.state import AgentState
from app.agents.router import ParentAgent
from app.agents.healthcare import HealthcareAgent
from app.agents.legal import LawyerAgent
from app.agents.software import SoftwareAgent
from app.agents.merger import MergeAgent
from app.guardrail.input_guardrail.injection_detector import InputInjectionDetector
from app.tools.tool_registry import shared_tool_list
from app.db.mongo import checkpointer

router_agent = ParentAgent()
healthcare_agent = HealthcareAgent()
legal_agent = LawyerAgent()
software_agent = SoftwareAgent()
merger_agent = MergeAgent()
input_injection_detector = InputInjectionDetector()

# tools_node = ToolNode(shared_tool_list)
healthcare_tools = ToolNode(
    shared_tool_list,
    messages_key="messages_healthcare"
)

legal_tools = ToolNode(
    shared_tool_list,
    messages_key="messages_legal"
)

software_tools = ToolNode(
    shared_tool_list,
    messages_key="messages_software"
)

async def call_input_injection_detector(state: AgentState):
    return await input_injection_detector.invoke(state)

async def call_router(state: AgentState):
    return await router_agent.invoke(state)
    
async def call_healthcare(state: AgentState):
    return await healthcare_agent.invoke(state)

async def call_legal(state: AgentState):
    return await legal_agent.invoke(state)

async def call_software(state: AgentState):
    return await software_agent.invoke(state)

async def call_merger(state: AgentState):
    return await merger_agent.invoke(state)

def route_decision(state: AgentState):
    """
    Determines next nodes after router execution.Supports parallel execution.
    """
    next_steps = state.get("next_steps", [])
    mapping = {
        "healthcare": "healthcare_node",
        "legal": "legal_node",
        "software": "software_node",
    }
    destinations = [
        mapping[step]
        for step in next_steps
        if step in mapping
    ]
    # If invalid or empty → end graph
    if not destinations:
        return END
    return destinations

def make_tool_condition(key: str):
    return lambda state: tools_condition(state, messages_key=key)

# Graph Construction
try:
    workflow = StateGraph(AgentState)

    # Node Defination
    workflow.add_node("input_security_node", call_input_injection_detector)
    workflow.add_node("router_node", call_router)
    workflow.add_node("healthcare_node", call_healthcare)
    workflow.add_node("legal_node", call_legal)
    workflow.add_node("software_node", call_software)
    # workflow.add_node("tools", tools_node)
    workflow.add_node("healthcare_tools", healthcare_tools)
    workflow.add_node("legal_tools", legal_tools)
    workflow.add_node("software_tools", software_tools)
    workflow.add_node("merger_node", call_merger)


    # Workflow
    workflow.set_entry_point("input_security_node")
    workflow.add_conditional_edges(
        "input_security_node",
        lambda state: state["security_verdict"],
        {
            "ALLOW": "router_node",
            "FLAG": "router_node",   # or send to review node
            "BLOCK": END,
        },
    )
    workflow.add_conditional_edges(
        "router_node",
        route_decision
    )
    workflow.add_conditional_edges(
        "healthcare_node",
        make_tool_condition("messages_healthcare"),
        {"tools": "healthcare_tools", END: "merger_node"},
    )
    workflow.add_conditional_edges(
        "legal_node",
        make_tool_condition("messages_legal"),
        {"tools": "legal_tools", END: "merger_node"},
    )
    workflow.add_conditional_edges(
        "software_node",
        make_tool_condition("messages_software"),
        {"tools": "software_tools", END: "merger_node"},
    )

    # ─── Tool → agent loopback (ReAct loop) ───────────────────────

    workflow.add_edge("healthcare_tools", "healthcare_node")
    workflow.add_edge("legal_tools", "legal_node")
    workflow.add_edge("software_tools", "software_node")
    workflow.add_edge("merger_node", END)

    app_graph = workflow.compile(checkpointer=checkpointer)

except Exception as e:
    print(e)
