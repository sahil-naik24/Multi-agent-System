from pathlib import Path
from typing import Dict

# In-memory cache
_PROMPT_CACHE: Dict[str, str] = {}

def load_prompt(prompt_name: str) -> str:
    """
    Load a markdown prompt file with caching.
    """
    if prompt_name in _PROMPT_CACHE:
        return _PROMPT_CACHE[prompt_name]

    base_path = Path(__file__).resolve().parent.parent / "prompts"
    file_path = base_path / f"{prompt_name}.md"
    print("prompt_path =", file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    prompt_text = file_path.read_text(encoding="utf-8")

    _PROMPT_CACHE[prompt_name] = prompt_text
    return prompt_text
