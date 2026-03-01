from app.tools.search import web_search_tool  # Your DuckDuckGo logic
from app.tools.rag import internal_knowledge_base

TOOL_REGISTRY = {
    "web_search": web_search_tool,
    "rag_tool": internal_knowledge_base,
}

AGENT_PERMISSIONS = {
    "healthcare": ["web_search", "rag_tool"],
    "software": ["web_search", "rag_tool"],
    "legal": ["web_search","rag_tool"]
}