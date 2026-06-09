from graph.state import AgentState

def analyze_code(state: AgentState):
    """
    Deterministic Critic: No LLM involved.
    If Docker executed cleanly, we immediately terminate the loop.
    If it failed, we categorize the error for the router.
    """
    print("--- CRITIC: Verifying Execution Deterministically ---")
    
    # 1. Immediate Pass Condition
    # If Docker says returncode == 0, it works. Stop overthinking.
    if state.get("execution_success"):
        print("--- CRITIC: Execution successful. Approving code. ---")
        return {
            "is_resolved": True,
            "critic_feedback": "Code executed successfully with no tracebacks.",
            "error_category": None
        }
    
    # 2. Failure Analysis
    error_traceback = state.get("error_traceback", "")
    print(f"--- CRITIC: Execution failed. Analyzing error... ---")
    
    # Simple keyword string matching is faster and more reliable than an LLM parser
    syntax_keywords = ["SyntaxError", "IndentationError", "NameError", "TypeError", "AttributeError"]
    
    if any(keyword in error_traceback for keyword in syntax_keywords):
        category = "syntax"
        feedback = f"Fix the following syntax/type error: {error_traceback}"
    else:
        category = "logic"
        feedback = f"The code failed to execute properly. Logic or runtime error: {error_traceback}"
        
    return {
        "is_resolved": False,
        "critic_feedback": feedback,
        "error_category": category
    }