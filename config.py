import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")

best_model="openai/gpt-oss-120b"
fastest_model="moonshotai/kimi-k2-instruct-0905"
GROQ_MODEL     =  fastest_model # 👈 change to your model
GROQ_BASE_URL  = "https://api.groq.com/openai/v1"