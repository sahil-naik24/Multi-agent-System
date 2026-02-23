import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = "./chroma_db"
CHROMA_DB_COLLECTION = "legal_documents"
LOCAL_DOCUMENT_DIRECTORY = "uploaded_pdfs"

AVAILABLE_AGENTS = {
    "healthcare": "Medical knowledge, clinical practice, diseases, diagnosis, treatment, patient care, public health, and healthcare systems. Responsible for reasoning about biological, physiological, and clinical implications.",
    "legal": "Software engineering, programming, AI systems, machine learning, computational models, system architecture, algorithms, and technical implementation. Responsible for reasoning about how systems are built and how computational mechanisms work.",
    "software": "Laws, regulations, constitutional matters, rights, compliance, liabilities, governance, and legal interpretation. Responsible for reasoning about legal implications, obligations, and statutory frameworks.",
}

AZURE_OPENAI_CM_API_KEY = os.getenv("AZURE_OPENAI_CM_API_KEY")
AZURE_OPENAI_CM_ENDPOINT = os.getenv("AZURE_OPENAI_CM_ENDPOINT") 
AZURE_OPENAI_CM_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CM_DEPLOYMENT_NAME") 
AZURE_OPENAI_CM_API_VERSION = os.getenv("AZURE_OPENAI_CM_API_VERSION") 
MODEL_TEMPERATURE = 0

AZURE_OPENAI_EMB_MODEL_NAME= os.getenv("AZURE_OPENAI_EMB_MODEL_NAME")
AZURE_OPENAI_EMB_DEPLOYMENT_NAME= os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT_NAME")
AZURE_OPENAI_EMB_ENDPOINT= os.getenv("AZURE_OPENAI_EMB_ENDPOINT")
AZURE_OPENAI_EMB_API_KEY= os.getenv("AZURE_OPENAI_EMB_API_KEY")
AZURE_OPENAI_EMB_API_VERSION= os.getenv("AZURE_OPENAI_EMB_API_VERSION")
