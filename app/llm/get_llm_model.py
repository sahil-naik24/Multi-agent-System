import app.core.config as CONFIG
from langchain_openai import AzureChatOpenAI

def get_chat_model():
    return AzureChatOpenAI(
            azure_endpoint=CONFIG.AZURE_OPENAI_CM_ENDPOINT,
            api_key=CONFIG.AZURE_OPENAI_CM_API_KEY,
            api_version=CONFIG.AZURE_OPENAI_CM_API_VERSION,
            deployment_name=CONFIG.AZURE_OPENAI_CM_DEPLOYMENT_NAME,
            temperature=CONFIG.MODEL_TEMPERATURE
        )