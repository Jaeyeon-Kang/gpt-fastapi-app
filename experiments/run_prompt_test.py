from prompt_template import prompts, system_roles, temperatures
from prompt_template import make_prompt
from main import log_chat
from openai import OpenAI
from datetime import datetime

client = OpenAI()

for prompt in prompts:
    for role in system_roles:
        for temp in temperatures:
            messages = make_prompt(prompt, role)

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=temp
            )

            reply = response.choices[0].message.content

            log_chat(
                timestamp=datetime.utcnow().isoformat(),
                user_input=prompt,
                system_role=role,
                temperature=temp,
                reply=reply
            )

            print(f"✅ [{temp}] {role[:25]:<25} → {reply[:60]}...")