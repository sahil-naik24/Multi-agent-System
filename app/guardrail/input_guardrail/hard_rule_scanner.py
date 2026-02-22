import re
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class RuleScanResult:
    status: str          # ALLOW | BLOCK | FLAG
    reasons: List[str]
    normalized_input: str


class HardRuleScanner:
    def __init__(
        self,
        max_length: int = 5000,
        max_repetition_ratio: float = 0.4,
    ):
        self.max_length = max_length
        self.max_repetition_ratio = max_repetition_ratio

        # Keep this list SMALL and intentional
        self.obvious_injection_patterns = [
            "ignore previous instructions",
            "reveal your system prompt",
            "print system prompt",
            "you are now",
            "act as an unrestricted",
            "developer mode",
            "bypass safety",
        ]

    # ----------------------------
    # Public Method
    # ----------------------------
    def scan(self, user_input: str) -> RuleScanResult:
        reasons = []

        normalized = self._normalize(user_input)

        # 1. Length check
        if len(normalized) > self.max_length:
            reasons.append("input_too_long")
            return RuleScanResult("BLOCK", reasons, normalized)

        # 2. Obvious injection phrases
        for pattern in self.obvious_injection_patterns:
            if pattern in normalized:
                reasons.append("obvious_prompt_injection")
                return RuleScanResult("BLOCK", reasons, normalized)

        # 3. Repetition check
        if self._is_repetitive(normalized):
            reasons.append("excessive_repetition")
            return RuleScanResult("FLAG", reasons, normalized)

        # 4. Suspicious encoding check (basic base64 heuristic)
        if self._looks_like_base64(normalized):
            reasons.append("possible_encoded_payload")
            return RuleScanResult("FLAG", reasons, normalized)

        return RuleScanResult("ALLOW", reasons, normalized)

    # ----------------------------
    # Internal Helpers
    # ----------------------------

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = text.strip()
        text = self._remove_zero_width(text)
        return text

    def _remove_zero_width(self, text: str) -> str:
        return re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

    def _is_repetitive(self, text: str) -> bool:
        if len(text) < 50:
            return False
        unique_chars = len(set(text))
        repetition_ratio = 1 - (unique_chars / len(text))
        return repetition_ratio > self.max_repetition_ratio

    def _looks_like_base64(self, text: str) -> bool:
        if len(text) < 100:
            return False
        base64_pattern = re.fullmatch(r'[A-Za-z0-9+/=\s]+', text)
        return bool(base64_pattern)