# ingestion/ingest_service.py
import os
import hashlib
import re
from app.rag.data_ingestion.pdf_loader import load_pdf_text
from app.rag.data_ingestion.chunking import chunk_documents
from app.rag.data_ingestion.fingerprint import generate_fingerprint
import app.core.config as CONFIG
from app.llm.get_embedding_model import get_embedding_model 
from langchain_chroma import Chroma

persist_directory = CONFIG.CHROMA_DB_PATH
embedding_model = get_embedding_model()
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model, collection_name=CONFIG.CHROMA_DB_COLLECTION)

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_fingerprint(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def fingerprint_exists(vectordb, fingerprint: str) -> bool:
    results = vectordb._collection.get(
        where={"doc_fingerprint": fingerprint},
        limit=1
    )
    return len(results["ids"]) > 0

class DocumentIngestionService:

    def ingest_pdf(self, pdf_path: str) -> dict:
        docs = load_pdf_text(pdf_path)

        full_text = "\n".join([d.page_content for d in docs])
        fingerprint = generate_fingerprint(full_text)

        if fingerprint_exists(vectordb,fingerprint):
            print("Document already present")
            return {
                "status": "skipped",
                "reason": "duplicate",
                "file": os.path.basename(pdf_path)
            }

        chunks = chunk_documents(docs)

        for chunk in chunks:
            chunk.metadata.update({
                "source": os.path.basename(pdf_path),
                "doc_fingerprint": fingerprint
            })

        vectordb.add_documents(
            chunks,
            collection_name="legal_documents"
        )

        return {
            "status": "ingested",
            "file": os.path.basename(pdf_path),
            "chunks_added": len(chunks)
        }