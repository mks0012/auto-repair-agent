from graph.workflow import app

def main():
    print("\n=== Autonomous AI Code Engine ===")
    print("Type 'exit' or 'quit' to shut down.\n")
    
    while True:
        user_input = input("System Prompt (What should I build?) > ")
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down engine...")
            break
            
        if not user_input.strip():
            continue
            
        # Initialize the global state for this run
        initial_state = {
            "user_prompt": user_input,
            "implementation_plan": "",
            "generated_code": "",
            "execution_success": False,
            "terminal_output": "",
            "error_traceback": None,
            "error_category": None,
            "critic_feedback": None,
            "loop_count": 0,
            "max_retries": 3 # Hard limit to prevent infinite token burning
        }
        
        print("\n[+] Initiating architecture and self-healing loop...\n")
        
        # Fire the graph execution
        final_state = app.invoke(initial_state)
        
        print("\n=== FINAL EXECUTION RESULT ===")
        if final_state.get("execution_success"):
            print("[SUCCESS] The code compiled and executed flawlessly.")
            print("\n--- Sandbox Output ---")
            print(final_state.get("terminal_output"))
            print("\n--- Final Hardened Codebase ---")
            print(final_state.get("generated_code"))
        else:
            print("[FAILED] Circuit breaker tripped. Maximum retries reached.")
            print("\n--- Final Error Traceback ---")
            print(final_state.get("error_traceback"))
            print("\n--- Code at Failure State ---")
            print(final_state.get("generated_code"))
        print("================================\n")

if __name__ == "__main__":
    main()