# ingestion/pdf_loader.py
from langchain_community.document_loaders import PyMuPDFLoader

def load_pdf_text(pdf_path: str) -> list:
    loader = PyMuPDFLoader(pdf_path)
    return loader.load()