# launch_chrome_debug.ps1
# 用于重启 Chrome 并开启调试端口 9222，以便 Playwright 连接

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "正在准备 Chrome 调试环境..." -ForegroundColor Cyan

# 1. 查找 Chrome 安装路径
$chromePath = ""
$possiblePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if (-not $chromePath) {
    Write-Error "未找到 Google Chrome 安装路径！请确认已安装 Chrome。"
    exit 1
}

Write-Host "找到 Chrome: $chromePath" -ForegroundColor Green

# 2. 关闭正在运行的 Chrome (强制关闭所有相关进程)
$chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($chromeProcesses) {
    Write-Host " 检测到 Chrome 正在运行，必须关闭才能加载默认配置。" -ForegroundColor Yellow
    Write-Host "正在强制关闭 Chrome..." -ForegroundColor Yellow
    cmd /c "taskkill /F /IM chrome.exe /T" | Out-Null
    cmd /c "taskkill /F /IM GoogleCrashHandler.exe /T" | Out-Null
    cmd /c "taskkill /F /IM GoogleCrashHandler64.exe /T" | Out-Null
    Start-Sleep -Seconds 3
}

# 3. 清理 SingletonLock (防止 Profile 锁定导致崩溃)
$userDataDir = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$lockFile = Join-Path $userDataDir "SingletonLock"
if (Test-Path $lockFile) {
    Write-Host "正在清理 Profile 锁文件..." -ForegroundColor Yellow
    Remove-Item -Path $lockFile -Force -ErrorAction SilentlyContinue
}

# 4. 以调试模式启动 Chrome
# 关键修改：不显式指定 --user-data-dir，让 Chrome 自动加载默认配置
# 这样可以避免路径空格和参数转义问题
$debugPort = 9222

Write-Host "正在启动 Chrome (调试端口: $debugPort)..." -ForegroundColor Green
Write-Host "加载默认配置..." -ForegroundColor Gray

# 使用 Start-Process 启动，仅传递调试端口参数
$procArgs = @("--remote-debugging-port=$debugPort")

try {
    Start-Process -FilePath $chromePath -ArgumentList $procArgs
} catch {
    Write-Error "启动 Chrome 失败: $_"
    exit 1
}

Write-Host "正在等待 Chrome 调试端口 ($debugPort) 就绪..." -ForegroundColor Yellow

# 循环检测端口是否开启 (使用静默方式)
$maxRetries = 30
$retryCount = 0
$portReady = $false

while ($retryCount -lt $maxRetries) {
    # 检查进程是否还在
    $proc = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Error "Chrome 进程意外退出！请检查是否被其他软件拦截。"
        exit 1
    }

    # 静默检测端口
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", $debugPort)
        $portReady = $true
        $tcp.Close()
        $tcp.Dispose()
        break
    } catch {
        # 端口未开启，继续等待
    }
    
    Start-Sleep -Seconds 1
    $retryCount++
    Write-Host "." -NoNewline -ForegroundColor Gray
}
Write-Host ""

if ($portReady) {
    Write-Host " Chrome 调试端口已就绪！" -ForegroundColor Green
    Write-Host " Chrome 已启动！请在打开的 Chrome 窗口中保持登录状态。" -ForegroundColor Green
    Write-Host "------------------------------------------------" -ForegroundColor Cyan
    exit 0
} else {
    Write-Error " Chrome 启动超时或调试端口未开启，请手动检查。"
    exit 1
}
