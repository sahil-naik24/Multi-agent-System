from typing import List
from langchain_core.tools import tool, BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from app.tools.search import web_search_tool  # Your DuckDuckGo logic
from app.tools.rag import internal_knowledge_base 


shared_tool_list = [web_search_tool, internal_knowledge_base]