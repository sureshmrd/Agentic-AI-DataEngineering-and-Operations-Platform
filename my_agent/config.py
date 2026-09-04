import os

from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3.8-27b")