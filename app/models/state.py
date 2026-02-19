from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage
import operator

from typing import TypedDict, List, Dict, Annotated
from langchain_core.messages import BaseMessage
import operator
from typing import Annotated, Dict, Optional

def merge_or_reset(current: Dict, update: Optional[Dict]) -> Dict:
    # 1. The "Reset" Signal: If the update is None, clear the dict
    if update is None:
        return {}
    
    # 2. The "Parallel" Logic: Otherwise, merge new data into old
    # This keeps your parallel agents safe
    return {**current, **update}

class AgentState(TypedDict, total=False):

    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    next_steps: List[str]
    sub_queries: Dict[str, str]
    agent_outputs: Annotated[Dict[str, str], merge_or_reset]
    final_output: str

