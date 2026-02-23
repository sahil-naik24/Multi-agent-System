import os
from dotenv import load_dotenv
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from langchain_core.messages import HumanMessage
from app.models.state import AgentState
from app.models.schemas import QueryRequest, QueryResponse
from app.rag.data_ingestion.ingestion_service import DocumentIngestionService
from app.workflow.graph import app_graph
import app.core.config as CONFIG

load_dotenv()

router = APIRouter()

os.makedirs(CONFIG.LOCAL_DOCUMENT_DIRECTORY, exist_ok=True)

@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    total_chunks = 0
    skipped_files = []
    ingested_files = []

    document_ingestion_service = DocumentIngestionService()

    for file in files:
        if not file.filename.endswith(".pdf"):
            continue

        save_path = os.path.join(CONFIG.LOCAL_DOCUMENT_DIRECTORY, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        response = document_ingestion_service.ingest_pdf(save_path)

    if not ingested_files and not skipped_files:
        raise HTTPException(status_code=400, detail="No valid PDFs uploaded")

    return response

@router.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    try:
        # 1. Initialize State
        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.query)],
            "query": request.query,
            "next_steps": [],
            "sub_queries": {},
            "agent_outputs": {},
            "final_output": "",
            "last_state":""
        }
        config = {"configurable": {"thread_id": request.session_id}}
        result = await app_graph.ainvoke(initial_state, config=config)
        # print(app_graph.get_state(config))

        # 3. Extract Output
        if isinstance(result, list):
            # Take the last state (usually the merged one)
            result = result[-1]

        final_answer = result.get("final_output", "No response generated.")        
        # print("last state =" ,final_answer["last_state"])
        return QueryResponse(
            final_response=final_answer,
            success=True
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
