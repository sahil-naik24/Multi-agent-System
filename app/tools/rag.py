from langchain_core.tools import tool
from app.db.vector_store import chroma_handler

@tool
def internal_knowledge_base(query: str) -> str:
    """
    Retrieve authoritative information from the internal knowledge base.

    This tool searches user-uploaded documents, organizational records,
    and internally approved reference materials across all supported domains
    (e.g., legal, healthcare, software, finance, technical documentation).

    Use this tool when:
    - You need verified, citation-ready information
    - The query requires domain-specific accuracy
    - The answer must be grounded in internal documents
    - You need authoritative definitions, policies, standards, or procedures

    The tool returns verbatim excerpts from relevant internal documents.

    If no relevant documents are found, the tool returns:
    NO_RELEVANT_DOCUMENTS
    """
    try:
        # chroma_handler should ideally return Document objects or text chunks
        docs = chroma_handler.query_documents(query)
        
        if not docs:
            return "NO_RELEVANT_DOCUMENTS"
        
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