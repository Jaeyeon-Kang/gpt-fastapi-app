from typing import List, Dict

def make_prompt(user_input: str, system_role: str = "You are a helpful assistant") -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_input}
    ]

prompts = [
    "How does it feel to be born as an AI?",
    "Explain the Industrial Revolution in an easy way."
]

system_roles = [
    "You are a helpful assistant.",
    "You are a stand-up comedian.",
    "You are a university professor."
]

temperatures = [0.2, 0.6, 0.9]

korean_prompts = [
    "AI로 태어난 기분이 어때?",
    "산업혁명에 대해 알기 쉽게 설명해줘."
]

korean_roles = [
    "넌 유능한 조수야.",
    "넌 유쾌한 개그맨이야.",
    "넌 대학 교수야."
]

korean_temperatures = [0.2, 0.6, 0.9]