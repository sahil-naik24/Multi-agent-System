from typing import Dict
import app.core.config as CONFIG
from app.guardrail.input_guardrail.hard_rule_scanner import HardRuleScanner
from app.guardrail.input_guardrail.llm_injection_classifier import LLMInjectionClassifier
from app.utils.agent_logger import AgentLogger

class InputInjectionDetector:
    def __init__(
        self,
        fail_closed: bool = True,
    ):
        self.rule_scanner = HardRuleScanner()
        self.llm_classifier = LLMInjectionClassifier()
        self.fail_closed = fail_closed
        self.allowed_verdicts = {"ALLOW", "BLOCK", "FLAG"}
        self.logger = AgentLogger(CONFIG.SECURITY_LOG_PATH)

    async def invoke(self, state: Dict) -> Dict:
        user_input = state.get("query", "")

        try:
            #Hard Rule Scan (sync, safe)
            rule_result = self.rule_scanner.scan(user_input)
            security_reasons= ",".join(rule_result.reasons)
            if rule_result.status == "BLOCK":
                log_data = {
                        "timestamp": self.logger.current_timestamp(),
                        "Security level": "User Input",
                        "security_verdict": "BLOCK",
                        "user_query": state["query"],
                        "detection_level": "HARD_SCAN",
                        "security_confidence": 1.0,
                        "normalized_input": rule_result.normalized_input
                                    }
                self.logger.log(log_data)
                return {
                    "normalized_input": rule_result.normalized_input,
                    "security_verdict": "BLOCK",
                    "security_reason": security_reasons,
                    "security_confidence": 1.0,
                    "detection_level": "HARD_SCAN",
                    "final_output": f"Malicious prompt detected. reasons:{security_reasons}"
                }

            # ----------------------------
            # 2️⃣ Async LLM Classifier
            # ----------------------------
            print("Execute llm classification")
            
            llm_result = await self.llm_classifier.classify(
                rule_result.normalized_input
            )
            print("rule_result llm scan=",llm_result)

            verdict = llm_result.get("verdict", "BLOCK")
            confidence = llm_result.get("confidence", 0.0)
            reason = llm_result.get("reason", "unknown")

            # ----------------------------
            # 3️⃣ Validate Output
            # ----------------------------
            if verdict not in self.allowed_verdicts:
                log_data = {
                        "timestamp": self.logger.current_timestamp(),
                        "Security level": "User Input",
                        "user_query": state["query"],
                        "security_verdict": verdict,
                        "reason" : reason,
                        "detection_level": "LLM_CLASSIFIER",
                        "normalized_input": rule_result.normalized_input
                                    }
                self.logger.log(log_data)
                raise ValueError("Invalid verdict from classifier")
            
            log_data = {
                        "timestamp": self.logger.current_timestamp(),
                        "Security level": "User Input",
                        "user_query": state["query"],
                        "security_verdict": verdict,
                        "reason" : reason,
                        "detection_level": "LLM_CLASSIFIER",
                        "security_confidence": confidence,
                        "normalized_input": rule_result.normalized_input
                                    }
            self.logger.log(log_data)

            return {
                "normalized_input": rule_result.normalized_input,
                "security_verdict": verdict,
                "security_reason": reason,
                "security_confidence": confidence,
                "detection_level": "LLM_CLASSIFIER",
                "final_output": f"Malicious prompt detected. reasons:{reason}"
            }

        except Exception as e:
            # ----------------------------
            # 4️⃣ Fail Closed
            # ----------------------------
            if self.fail_closed:
                return {
                    "security_verdict": "BLOCK",
                    "security_reason": f"security_node_error:{str(e)}",
                    "security_confidence": 0.0,
                }
            else:
                raise