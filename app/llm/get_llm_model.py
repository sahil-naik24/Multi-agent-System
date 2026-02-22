import os
from dotenv import load_dotenv
from functools import lru_cache
from langchain_openai import AzureChatOpenAI

load_dotenv()

@lru_cache()
def get_chat_model():
    return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CM_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CM_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CM_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_CM_DEPLOYMENT_NAME"),
            temperature=os.getenv("MODEL_TEMPERATURE")
        )


def get_chat_model_stream(streaming: bool = False, callbacks=None):
    return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CM_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CM_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CM_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_CM_DEPLOYMENT_NAME"),
            temperature=os.getenv("MODEL_TEMPERATURE")
        )