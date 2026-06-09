import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: GROQ_API_KEY is missing from your environment variables. "
        "Create a .env file in the root directory and add: GROQ_API_KEY=your_key_here"
    )

# Updated Model definitions for active Groq endpoints
# Updated Model definitions for active Groq endpoints
PLANNER_MODEL = "llama-3.3-70b-versatile"  
CODER_MODEL = "llama-3.3-70b-versatile"    
CRITIC_MODEL = "llama-3.3-70b-versatile"   # UPGRADED: Need high reasoning for QA