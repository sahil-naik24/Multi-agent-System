import os
from dotenv import load_dotenv
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from langchain_core.messages import HumanMessage
from app.models.state import AgentState
from app.models.schemas import QueryRequest, QueryResponse
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.workflow.graph import app_graph
import app.core.config as CONFIG
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

persist_directory = CONFIG.CHROMA_DB_PATH
embedding_model = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMB_MODEL_NAME"),           
    deployment=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT_NAME"),      
    azure_endpoint=os.getenv("AZURE_OPENAI_EMB_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMB_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_EMB_API_VERSION")
)
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model, collection_name=CONFIG.CHROMA_DB_COLLECTION)

router = APIRouter()

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload multiple PDFs, save to folder, and ingest into ChromaDB"""
    total_chunks = 0
    saved_files = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            continue  # skip non-PDFs

        # Save uploaded PDF to the upload folder
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(save_path)

        # Load PDF and split into chunks
        loader = PyMuPDFLoader(save_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)

        # Add chunks to ChromaDB
        vectordb.add_documents(chunks, collection_name="legal_documents")
        total_chunks += len(chunks)

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid PDF files uploaded.")

    return {
        "message": f"{total_chunks} chunks ingested from {len(saved_files)} files.",
        "files": saved_files
    }

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
