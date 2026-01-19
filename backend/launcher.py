import os
import sys
import time
import subprocess
import socket
import shutil

def find_chrome_path():
    """查找 Chrome 可执行文件路径"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def is_port_open(host, port):
    """检查端口是否开启"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def kill_chrome():
    """强制关闭 Chrome 进程"""
    print("[Launcher] 正在关闭旧的 Chrome 进程...")
    try:
        subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run("taskkill /F /IM GoogleCrashHandler.exe /T", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(2)
    except Exception as e:
        print(f"[Launcher] 关闭进程时出错 (可忽略): {e}")

def main():
    print("-" * 50)
    print("[Launcher] 正在启动 Chrome 调试环境 (Python版)...")
    
    # 1. 查找 Chrome
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("[Launcher] ❌ 未找到 Chrome 安装路径！")
        sys.exit(1)
    print(f"[Launcher] 找到 Chrome: {chrome_path}")

    # 2. 清理环境
    kill_chrome()

    # 3. 准备参数
    # 不显式指定 user-data-dir，让 Chrome 自动加载默认配置
    # 这样可以避免路径错误，且符合用户“使用默认浏览器”的需求
    debug_port = 9222
    
    print(f"[Launcher] 调试端口: {debug_port}")

    # 4. 启动进程
    # 使用 subprocess.Popen 列表传参
    cmd = [
        chrome_path,
        f"--remote-debugging-port={debug_port}"
    ]
    
    try:
        # shell=False 确保参数不被 shell 再次解析
        process = subprocess.Popen(cmd, shell=False)
        print("[Launcher] Chrome 进程已启动")
    except Exception as e:
        print(f"[Launcher] ❌ 启动失败: {e}")
        sys.exit(1)

    # 5. 等待端口就绪
    print(f"[Launcher] 正在等待端口 {debug_port} 就绪...")
    max_retries = 20
    for i in range(max_retries):
        # 检查进程是否意外退出
        if process.poll() is not None:
            print(f"\n[Launcher] ❌ Chrome 进程意外退出 (Exit Code: {process.returncode})")
            print("可能原因：")
            print("1. 旧的 Chrome 进程未完全关闭 (请尝试在任务管理器中强制结束所有 chrome.exe)")
            print("2. 配置文件被锁定")
            sys.exit(1)

        if is_port_open("127.0.0.1", debug_port):
            print(f"\n[Launcher] ✅ Chrome 调试端口已就绪！")
            print("-" * 50)
            sys.exit(0)
        print(".", end="", flush=True)
        time.sleep(1)
    
    print("\n[Launcher] ❌ 等待超时！端口未开启。")
    print("可能原因：")
    print("1. Chrome 进程被残留的后台进程阻塞 (请尝试重启电脑)")
    print("2. 权限不足")
    sys.exit(1)

if __name__ == "__main__":
    main()
