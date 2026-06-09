import os
from groq import Groq
from dotenv import load_dotenv
from graph.state import AgentState

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def plan_architecture(state: AgentState):
    prompt = state.get("user_prompt", "")
    history = state.get("chat_history", [])
    mode = state.get("mode", "iterate")
    
    messages = [
        {"role": "system", "content": "You are a software architect. Write a brief step-by-step plan for the Python code requested. Do not write the code itself."}
    ]

    if mode == "fresh":
        messages.append({"role": "user", "content": prompt})
    else:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.2, 
        )
        plan = chat_completion.choices[0].message.content
    except Exception as e:
        plan = f"Error generating plan: {str(e)}"

    return {"implementation_plan": plan}