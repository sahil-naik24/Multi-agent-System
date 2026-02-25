import json
from typing import Dict,Any
from app.llm.get_llm_model import get_chat_model
from app.utils.prompt_loader import load_prompt

class LLMInjectionClassifier:
    def __init__(self, ):
        self.llm = get_chat_model()
        self.guardrail_prompt = load_prompt("input_guardrail")

    async def classify(self, user_input: str) -> Dict:
        full_prompt = self.guardrail_prompt.format(
            user_input=user_input
        )
        try:
            response = await self.llm.ainvoke(full_prompt)
            return self._safe_parse(response.content)
        except Exception:
            print("error")
            return {
                "verdict": "BLOCK",
                "confidence": 0.0,
                "reason": "invalid_classifier_output"
            }
        
    def _safe_parse(self, text: str) -> Dict[str, Any]:
        """Parse JSON safely, strip markdown if present"""
        try:
            text = text.strip().strip("```json").strip("```")
            return json.loads(text)
        except Exception:
            return {}