@echo off
echo ==================================================
echo   小红书提取工具 - Chrome 调试启动器 (稳定版)
echo ==================================================
echo.

:: 1. 定义路径
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
:: 使用临时目录，避开默认目录的锁定问题
set "TEMP_USER_DATA=%TEMP%\xhs_chrome_debug"

echo [*] 准备环境...
if exist "%TEMP_USER_DATA%\SingletonLock" del /f /q "%TEMP_USER_DATA%\SingletonLock" 2>nul

echo [*] 正在启动 Chrome...
echo [!] 提示：启动后请在窗口中登录一次小红书。
echo.

:: 2. 启动命令 (使用双引号包裹路径和参数，确保兼容性)
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%TEMP_USER_DATA%" --no-first-run --no-default-browser-check

echo [OK] 浏览器已启动。
echo [OK] 请确认 Chrome 窗口已打开，然后运行 start.ps1。
echo.
pause
