from typing import List, Dict

def make_prompt(user_input: str, system_role: str = "You are a helpful assistant") -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_input}
    ]

# 실험용 사용자 입력들
prompts = [
    "What is AI?",
    "Explain black holes.",
    "Tell me a joke.",
    "Summarize the Industrial Revolution in 1 sentence."
]

# GPT의 system 역할 캐릭터
system_roles = [
    "You are a helpful assistant.",
    "You are a stand-up comedian.",
    "You are a university professor.",
    "You are a compassionate therapist.",
    "You should make a short answer."
]

# 창의성 정도 설정값
temperatures = [0.3, 0.7, 0.9]

# Korean version prompts
korean_prompts = [
    "AI가 뭐야?",
    "블랙홀은 어떻게 작동해?",
    "재밌는 농담 하나 해줘.",
    "산업혁명을 한 문장으로 요약해줘."
]

korean_roles = [
    "넌 유능한 조수야.",
    "넌 유쾌한 개그맨이야.",
    "넌 대학 교수야.",
    "넌 따뜻한 심리상담가야.",
    "간결하게 대답해줘."
]

korean_temperatures = [0.3, 0.7, 0.9]