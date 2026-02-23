# ingestion/chroma_repo.py
from langchain.vectorstores import Chroma

class ChromaRepository:
    def __init__(self, vectordb: Chroma):
        self.vectordb = vectordb
        self.collection = vectordb._collection

    def fingerprint_exists(self, fingerprint: str) -> bool:
        results = self.collection.get(
            where={"doc_fingerprint": fingerprint},
            limit=1
        )
        return len(results["ids"]) > 0

    def add_chunks(self, chunks):
        self.vectordb.add_documents(chunks)