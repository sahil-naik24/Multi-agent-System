from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool

# Initialize the wrapper once at the module level (Singleton-ish)
search_wrapper = DuckDuckGoSearchAPIWrapper()

@tool
def web_search_tool(query: str) -> str:
    """
    Search the web for up-to-date information, news, or specific factual data.
    Use this tool when internal knowledge is insufficient or current events are required.
    
    Args:
        query: The specific search string.
    """
    try:
        # We remove the hardcoded "medical" prefix to make it general-purpose.
        # The LLM (Healthcare, Legal, or Software) will naturally provide the 
        # domain context in the 'query' parameter based on its persona.
        results = search_wrapper.results(query, max_results=5)

        if not results:
            return f"No relevant information found for: {query}"

        # Improved formatting for LLM readability
        formatted_list = []
        for r in results:
            entry = (
                f"Source: {r.get('title', 'N/A')}\n"
                f"Link: {r.get('link', 'N/A')}\n"
                f"Summary: {r.get('snippet', 'No snippet available.')}"
            )
            formatted_list.append(entry)

        return "\n\n---\n\n".join(formatted_list)

    except Exception as e:
        return f"Error performing search: {str(e)}"