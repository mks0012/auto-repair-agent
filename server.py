import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from graph.workflow import app as workflow_app

app = FastAPI()

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        raw_data = await websocket.receive_text()
        payload = json.loads(raw_data)
        
        # EXTRACT EVERYTHING FROM REACT
        chat_history = payload.get("history", [])
        current_prompt = payload.get("prompt", "")
        current_code = payload.get("current_code", "") 
        current_mode = payload.get("mode", "iterate") # CAUGHT THE TOGGLE

        # HYDRATE THE STATE
        initial_state = {
            "chat_history": chat_history,
            "user_prompt": current_prompt,
            "mode": current_mode,
            "implementation_plan": "",
            "generated_code": current_code, 
            "execution_success": False,
            "terminal_output": "",
            "error_traceback": None,
            "error_category": None,
            "critic_feedback": None,
            "is_resolved": False,
            "loop_count": 0,
            "max_retries": 3 
        }

        # EXECUTE LANGGRAPH
        for event in workflow_app.stream(initial_state):
            for node_name, state_update in event.items():
                await websocket.send_json({
                    "type": "node_update",
                    "node": node_name.upper(),
                    "state": state_update
                })
                
        await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)