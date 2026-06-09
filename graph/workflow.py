from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from nodes.planner import plan_architecture
from nodes.generator import write_code
from sandbox.docker_runtime import execute_code_in_sandbox
from nodes.critic import analyze_code

def general_query_node(state: AgentState):
    return {
        "terminal_output": "[ALE System] General query detected. I am configured to write code. Please provide a coding task.",
        "generated_code": state.get("generated_code", "") 
    }

def route_prompt(state: AgentState):
    prompt = state["user_prompt"].lower()
    mode = state.get("mode", "iterate") # Fetch the explicit mode from the UI
    
    # CONTEXT AWARENESS: Only assume iteration if mode is ACTUALLY set to iterate
    if mode == "iterate" and len(state.get("chat_history", [])) > 0:
        print("--- ROUTER: Active history detected (Iterate Mode). Routing to PLANNER ---")
        return "planner"
        
    action_words = [
        "code", "script", "function", "write", "logic", "python", "fix", 
        "add", "change", "update", "make", "remove", "now", "multiply", "divide"
    ]
    
    if any(word in prompt for word in action_words):
        print("--- ROUTER: Keyword detected. Routing to PLANNER ---")
        return "planner"
        
    print("--- ROUTER: General chat detected. Routing to GENERAL ---")
    return "general"

def route_post_critic(state: AgentState):
    if state.get("is_resolved", False):
        return END
    
    loop_count = state.get("loop_count", 0)
    max_retries = state.get("max_retries", 3)

    if loop_count >= max_retries:
        return END
        
    if state.get("error_category") == "syntax":
        return "generator"
    else:
        return "planner"

# Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_architecture)
workflow.add_node("generator", write_code)
workflow.add_node("executor", execute_code_in_sandbox)
workflow.add_node("critic", analyze_code)
workflow.add_node("general", general_query_node)

# Wiring
workflow.add_conditional_edges(START, route_prompt)
workflow.add_edge("planner", "generator")
workflow.add_edge("generator", "executor")
workflow.add_edge("executor", "critic")
workflow.add_conditional_edges("critic", route_post_critic)
workflow.add_edge("general", END)

app = workflow.compile()