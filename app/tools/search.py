# search.py

from langchain.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

search_wrapper = DuckDuckGoSearchAPIWrapper()

@tool
def medical_search(query: str) -> str:
    """
    Search for medical information related to a health query.
    Use this when you need factual or up-to-date medical information.
    """
    refined_query = f"{query} medical information"
    results = search_wrapper.results(refined_query, max_results=3)

    formatted = "\n\n".join(
        f"Title: {r['title']}\n"
        f"URL: {r['link']}\n"
        f"Snippet: {r['snippet']}"
        for r in results
    )

    return formatted
