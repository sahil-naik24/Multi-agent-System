# RAG implementation

from app.db.vector_store import chroma_handler

class LegalRetriever:
    def retrieve(self, query: str) -> str:
        """
        Retrieves relevant legal documents and formats them as a context string.
        """
        try:
            docs = chroma_handler.query_documents(query)
            print(docs)
            
            if not docs:
                return "No relevant legal documents found in the database."
            
            # Format documents into a single context block
            formatted_context = "\n\n".join([f"Document Chunk {i+1}: {doc}" for i, doc in enumerate(docs)])
            return formatted_context
            
        except Exception as e:
            return f"Error retrieving documents: {str(e)}"