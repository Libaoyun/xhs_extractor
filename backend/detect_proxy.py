import urllib.request
import os

print("[*] 正在检测系统代理设置...")
proxies = urllib.request.getproxies()
print(f"[*] 检测到的代理: {proxies}")

# 尝试构建 google-genai 兼容的配置
http_proxy = proxies.get('http') or proxies.get('https')
if http_proxy:
    print(f"[*] 建议使用的代理地址: {http_proxy}")
else:
    print("[!] 未检测到系统代理。如果您在中国大陆，请确保开启了代理软件（如 Clash/V2Ray）。")

# 模拟 ai_service 中的逻辑
proxy_env = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
print(f"[*] 环境变量中的代理 (当前): {proxy_env}")
