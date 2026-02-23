# ingestion/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(docs, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return splitter.split_documents(docs)