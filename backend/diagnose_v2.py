import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
proxy = os.getenv("HTTP_PROXY")

print(f"[*] API Key: {api_key[:10]}...")
print(f"[*] Proxy: {proxy}")

try:
    genai.configure(api_key=api_key)
    
    print("[*] 正在获取可用模型列表...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            
except Exception as e:
    print(f"[!] 错误: {str(e)}")
