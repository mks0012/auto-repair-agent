from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    chat_history: List[Dict[str, str]]
    user_prompt: str
    mode: str 
    implementation_plan: str
    generated_code: str
    execution_success: bool
    terminal_output: str
    error_traceback: Optional[str]
    error_category: Optional[str]
    critic_feedback: Optional[str]
    is_resolved: bool
    loop_count: int
    max_retries: int