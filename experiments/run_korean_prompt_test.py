from prompt_template import korean_prompts, korean_roles, korean_temperatures, make_prompt
from main import log_chat
from openai import OpenAI
from datetime import datetime
import os
import csv

client = OpenAI()

# 한글용 로그 저장 따로 구성
def log_chat_ko(timestamp, user_input, system_role, temperature, reply):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/chat_logs_ko.csv"
    log_exists = os.path.isfile(log_path)

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "user_input", "system_role", "temperature", "reply"
        ])
        if not log_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "user_input": user_input,
            "system_role": system_role,
            "temperature": temperature,
            "reply": reply
        })

# 실험 실행
for prompt in korean_prompts:
    for role in korean_roles:
        for temp in korean_temperatures:
            messages = make_prompt(prompt, role)

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=temp
            )

            reply = response.choices[0].message.content

            log_chat_ko(
                timestamp=datetime.utcnow().isoformat(),
                user_input=prompt,
                system_role=role,
                temperature=temp,
                reply=reply
            )

            print(f"🇰🇷 [{temp}] {role[:20]:<20} → {reply[:50]}...")