"""
LangGraph Construction
Multi-Agent Healthcare / Legal / Software System
With MongoDB Checkpointer
"""

from langgraph.graph import StateGraph, END
from app.models.state import AgentState

# Agents
from app.agents.router import ParentAgent
from app.agents.healthcare import HealthcareAgent
from app.agents.legal import LawyerAgent
from app.agents.software import SoftwareAgent
from app.agents.merger import MergeAgent

# Checkpointer
from app.db.mongo import checkpointer

router_agent = ParentAgent()
healthcare_agent = HealthcareAgent()
legal_agent = LawyerAgent()
software_agent = SoftwareAgent()
merger_agent = MergeAgent()

async def call_router(state: AgentState):
    """
    Router determines:
    - validity
    - next_steps (domains)
    - sub-queries
    """
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
    Determines next nodes after router execution.
    Supports parallel execution.
    """
    print("enter route decision")
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


# --------------------------------------------------
# Graph Construction
# --------------------------------------------------
try:
    workflow = StateGraph(AgentState)

    workflow.add_node("router_node", call_router)
    workflow.add_node("healthcare_node", call_healthcare)
    workflow.add_node("legal_node", call_legal)
    workflow.add_node("software_node", call_software)
    workflow.add_node("merger_node", call_merger)

    workflow.set_entry_point("router_node")

    workflow.add_conditional_edges(
        "router_node",
        route_decision
    )
    workflow.add_edge("healthcare_node", "merger_node")
    workflow.add_edge("legal_node", "merger_node")
    workflow.add_edge("software_node", "merger_node")
    workflow.add_edge("merger_node", END)

    app_graph = workflow.compile(checkpointer=checkpointer)

except Exception as e:
    print(e)
