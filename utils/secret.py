import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SECRET = os.getenv("SECRET")
if not SECRET:
    raise ValueError("CRITICAL: SECRET environment variable is not set. Please set it in .env file.")
