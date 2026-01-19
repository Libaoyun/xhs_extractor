import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(('127.0.0.1', port)) == 0

common_ports = [7890, 1080, 10808, 10809]
found_proxy = None

print("[*] 正在扫描常用代理端口...")
for port in common_ports:
    if check_port(port):
        print(f"[OK] 发现本地开放端口: {port}")
        found_proxy = f"http://127.0.0.1:{port}"
        break

if found_proxy:
    print(f"[*] 建议使用的代理: {found_proxy}")
else:
    print("[!] 未发现常用代理端口。")
