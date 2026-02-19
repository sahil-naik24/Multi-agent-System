import json
import time
from datetime import datetime
from typing import Dict, Any


class AgentLogger:
    def __init__(self, file_path: str = "router_logs.jsonl"):
        self.file_path = file_path

    def log(self, data: Dict[str, Any]) -> None:
        """Append structured router log as JSONL"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    @staticmethod
    def current_timestamp() -> str:
        return datetime.utcnow().isoformat() + "Z"