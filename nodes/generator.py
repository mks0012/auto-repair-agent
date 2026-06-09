import os
from groq import Groq
from dotenv import load_dotenv
from graph.state import AgentState

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def write_code(state: AgentState):
    history = state.get("chat_history", [])
    prompt = state.get("user_prompt", "")
    current_code = state.get("generated_code", "") 
    mode = state.get("mode", "iterate")
    critic_feedback = state.get("critic_feedback")
    current_loop = state.get("loop_count", 0) + 1
    
    system_prompt = (
        "You are an autonomous Python coding agent. Output ONLY valid, runnable Python code. "
        "CRITICAL RULE: NEVER use input(). Docker is headless and has no keyboard. "
        "Hardcode test variables or use function arguments instead. "
        "Do not wrap code in markdown. No explanations."
    )
    
    messages = [{"role": "system", "content": system_prompt}]

    if critic_feedback and current_code:
        messages.append({
            "role": "user", 
            "content": f"Your previous code failed in execution. \n[BROKEN CODE]\n{current_code}\n\n[ERROR LOG]\n{critic_feedback}\n\nFix the code so it executes cleanly."
        })
    else:
        if mode == "fresh":
            messages.append({"role": "user", "content": prompt})
        else:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            if current_code:
                messages.append({"role": "user", "content": f"Current Code in editor:\n{current_code}\n\nUser Prompt: {prompt}"})
            else:
                messages.append({"role": "user", "content": prompt})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.1, 
        )
        
        generated_text = chat_completion.choices[0].message.content
        
        if generated_text.startswith("```python"):
            generated_text = generated_text[9:]
        elif generated_text.startswith("```"):
            generated_text = generated_text[3:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]
            
        generated_text = generated_text.strip()
        
    except Exception as e:
        generated_text = f'print("""Groq API Error: {str(e)}""")'

    return {
        "generated_code": generated_text,
        "loop_count": current_loop
    }