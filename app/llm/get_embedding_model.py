import app.core.config as CONFIG
from langchain_openai import AzureOpenAIEmbeddings


def get_embedding_model():
    return AzureOpenAIEmbeddings(
        model=CONFIG.AZURE_OPENAI_EMB_MODEL_NAME,           # optional in Azure
        deployment=CONFIG.AZURE_OPENAI_EMB_DEPLOYMENT_NAME,      # Azure deployment name
        azure_endpoint=CONFIG.AZURE_OPENAI_EMB_ENDPOINT,
        api_key=CONFIG.AZURE_OPENAI_EMB_API_KEY,
        openai_api_version=CONFIG.AZURE_OPENAI_EMB_API_VERSION
        )