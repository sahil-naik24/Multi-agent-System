# ChromaDB connection logic
import app.core.config as CONFIG
from app.llm.get_embedding_model import get_embedding_model 
from langchain_chroma import Chroma

class ChromaHandler:
    def __init__(self):
        # Use LangChain's Chroma wrapper with Azure embeddings
        self.embedding_fn = get_embedding_model()
        # Create or load a persistent collection
        self.vectorstore = Chroma(
            collection_name=CONFIG.CHROMA_DB_COLLECTION,
            embedding_function=self.embedding_fn,
            persist_directory=CONFIG.CHROMA_DB_PATH
        )

    def add_documents(self, documents: list[str], ids: list[str]):
        """
        Adds legal documents to the vector store.
        """
        self.vectorstore.add_texts(texts=documents, ids=ids)
        self.vectorstore.persist()  # ensure data is saved

    def query_documents(self, query_text: str, n_results: int = 10):
        """
        Performs a semantic search.
        """
        results = self.vectorstore.similarity_search(
            query_text, k=n_results
        )
        # Returns just the texts
        return [doc.page_content for doc in results]

# Singleton instance
chroma_handler = ChromaHandler()
