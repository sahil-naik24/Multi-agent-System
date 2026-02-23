import os
from fastapi import FastAPI
import uvicorn
import app.core.config as CONFIG
from app.rag.data_ingestion.ingestion_service import DocumentIngestionService
import app
from app.api.routes import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    service = DocumentIngestionService()
    for filename in os.listdir(CONFIG.LOCAL_DOCUMENT_DIRECTORY):
        service.ingest_pdf(os.path.join(CONFIG.LOCAL_DOCUMENT_DIRECTORY, filename))

    print("✅ Startup ingestion completed")

    yield


app = FastAPI(title="Multi-Agent Intelligent System",lifespan=lifespan
)


# Include the router
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)