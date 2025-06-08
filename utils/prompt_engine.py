# utils/prompt_engine.py

from typing import List, Dict

def make_prompt(user_input: str, system_role: str = "You are a helpful assistant") -> List[Dict[str, str]]:
    """
    system_role 예시:
    - 사용자가 질문하고 명확한 설명을 원하는 상황: "You are a helpful assistant."
    - 사용자가 감정적인 위로를 원하는 상황: "You are a compassionate counselor."
    - 사용자가 코딩 조언을 원하는 상황: "You are a senior software engineer."
    """
    return [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_input}
    ]
