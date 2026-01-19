import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"[*] 使用 API Key: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key)
    print("[*] 正在获取模型列表...")
    models = client.models.list()
    for m in models:
        print(f" - {m.name}")
except Exception as e:
    print(f"[!] 错误: {str(e)}")
