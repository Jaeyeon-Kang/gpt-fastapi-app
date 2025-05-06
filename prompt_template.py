def make_prompt(user_input: str):
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]