from graph.state import AgentState

def router_node(state: AgentState):
    prompt = state.get("user_prompt", "")
    # Simple logic: Ask the LLM to classify intent
    # If it's a coding question, return "code". Otherwise, "chat".
    # For this implementation, we use a simple heuristic:
    if any(word in prompt.lower() for word in ["write", "function", "code", "python", "script"]):
        return {"intent": "code"}
    return {"intent": "chat"}