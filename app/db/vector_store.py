# ChromaDB connection logic
import os
from dotenv import load_dotenv
import app.core.config as CONFIG
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

class ChromaHandler:
    def __init__(self):
        # Use LangChain's Chroma wrapper with Azure embeddings
        self.embedding_fn =AzureOpenAIEmbeddings(
        model=os.getenv("AZURE_OPENAI_EMB_MODEL_NAME"),           # optional in Azure
        deployment=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT_NAME"),      # Azure deployment name
        azure_endpoint=os.getenv("AZURE_OPENAI_EMB_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_EMB_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_EMB_API_VERSION")
        )

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
        print("query result = ",results)
        # Returns just the texts
        return [doc.page_content for doc in results]

# Singleton instance
chroma_handler = ChromaHandler()
