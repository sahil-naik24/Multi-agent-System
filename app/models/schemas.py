from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class AgentLog(BaseModel):
    agent_name: str
    response: str

class QueryResponse(BaseModel):
    final_response: str
    execution_path: List[str] = [] 
    success: bool = True
