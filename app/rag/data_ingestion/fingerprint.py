# ingestion/fingerprint.py
import hashlib
import re

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_fingerprint(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()