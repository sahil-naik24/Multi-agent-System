from langchain_core.tools import tool
from app.db.vector_store import chroma_handler

@tool
def internal_knowledge_base(query: str) -> str:
    """
    Search the internal vector database for authoritative information. 
    Contains legal precedents, healthcare protocols, and internal technical documentation.
    Use this tool when you need verified, non-public data.
    """
    try:
        # chroma_handler should ideally return Document objects or text chunks
        docs = chroma_handler.query_documents(query)
        
        if not docs:
            return f"No internal records found related to: {query}"
        
        # We improve formatting to include markers that help the LLM cite sources
        formatted_chunks = []
        for i, doc in enumerate(docs):
            # If your chroma_handler returns objects, use doc.page_content
            # If it returns strings, use doc directly
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            
            chunk = (
                f"--- INTERNAL RECORD CHUNK {i+1} ---\n"
                f"{content}\n"
            )
            formatted_chunks.append(chunk)
            
        return "\n".join(formatted_chunks)
            
    except Exception as e:
        return f"Knowledge Base Retrieval Error: {str(e)}"