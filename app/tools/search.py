# search.py

from langchain.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

search_wrapper = DuckDuckGoSearchAPIWrapper()

@tool
def medical_search(query: str) -> str:
    """
    Retrieve reliable medical information relevant to a health-related query.
    Use this tool when factual, up-to-date, or condition-specific information is required.
    """
    refined_query = f"{query} medical health information"

    results = search_wrapper.results(refined_query, max_results=5)

    if not results:
        return "No relevant medical information found."

    formatted = "\n\n".join(
        f"Title: {r['title']}\n"
        f"URL: {r['link']}\n"
        f"Snippet: {r['snippet']}"
        for r in results
    )
