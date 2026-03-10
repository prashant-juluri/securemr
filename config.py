from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AI_MODELS = {
    "explain": os.getenv("AI_MODEL_EXPLAIN", "gpt-4o"),
    "risk": os.getenv("AI_MODEL_RISK", "gpt-4o-mini"),
    "fix": os.getenv("AI_MODEL_FIX", "gpt-4o")
}