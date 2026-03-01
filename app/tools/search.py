from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool

# Initialize the wrapper once at the module level (Singleton-ish)
search_wrapper = DuckDuckGoSearchAPIWrapper()

@tool
def web_search_tool(query: str) -> str:
    """
    Retrieve publicly available information from the web.
    This tool is domain-agnostic and may be used by any agent
    The tool returns summarized excerpts from multiple web sources.
    If no relevant results are found, the tool returns:
    NO_RELEVANT_RESULTS
    """
    try:
        results = search_wrapper.results(query, max_results=5)

        if not results:
            return f"No relevant information found for: {query}"

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