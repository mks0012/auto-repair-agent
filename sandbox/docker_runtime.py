import subprocess
import tempfile
import os
from graph.state import AgentState

def execute_code_in_sandbox(state: AgentState):
    """
    Executes Python code in a highly restricted, isolated Docker container.
    Acts as a proper LangGraph node by accepting and returning state dictionaries.
    """
    # 1. Extract the raw string from the LangGraph state dictionary
    generated_code = state.get("generated_code", "")

    # 2. Write the code to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(generated_code)
        temp_file_path = temp_file.name

    try:
        command = [
            "docker", "run",
            "--rm", "--network", "none", "--cpus", "0.5", "--memory", "128m",
            "--pids-limit", "50", "--read-only",
            "-v", f"{temp_file_path}:/app/script.py:ro",
            "python:3.10-slim", "python", "/app/script.py"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5 
        )

        # 3. Return a dictionary that maps perfectly back to AgentState
        if result.returncode == 0:
            return {
                "execution_success": True,
                "terminal_output": result.stdout.strip() or "Execution finished with no output.",
                "error_traceback": None
            }
        else:
            return {
                "execution_success": False,
                "terminal_output": result.stdout.strip(),
                "error_traceback": result.stderr.strip()
            }

    except subprocess.TimeoutExpired:
        return {
            "execution_success": False,
            "terminal_output": "",
            "error_traceback": "Execution Failed: Time limit exceeded (5 seconds)."
        }
    
    except Exception as e:
        return {
            "execution_success": False,
            "terminal_output": "",
            "error_traceback": f"Sandbox Infrastructure Error: {str(e)}"
        }
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)