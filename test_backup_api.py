
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY_2", "").strip()
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

if not api_key:
    print("ERROR: GEMINI_API_KEY_2 is missing from .env")
else:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: Backup API working",
        )
        print("SUCCESS:", response.text)
    except Exception as exc:
        print("BACKUP API FAILED")
        print(type(exc).__name__, str(exc)[:1200])
