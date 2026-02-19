from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Multi-Agent Intelligent System")

# Include the router
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)