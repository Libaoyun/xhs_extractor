# start.ps1 - 小红书提取工具服务启动脚本

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "🚀 正在启动后端与前端服务..." -ForegroundColor Cyan
Write-Host "提示：请确保您已经运行了 launch_chrome.bat 并打开了浏览器。" -ForegroundColor Yellow

# 1. 启动后端 (在新窗口中)
Write-Host "[1/2] 正在启动后端服务..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"

# 2. 启动前端 (在新窗口中)
Write-Host "[2/2] 正在启动前端服务..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "------------------------------------------------" -ForegroundColor Green
Write-Host "✅ 服务启动指令已发送！" -ForegroundColor Green
Write-Host "后端 API: http://localhost:8000" -ForegroundColor Gray
Write-Host "前端 页面: http://localhost:3000" -ForegroundColor Gray
Write-Host "------------------------------------------------" -ForegroundColor Green
Write-Host "请在弹出的两个新窗口中查看运行日志。" -ForegroundColor Yellow

# 保持窗口开启
Read-Host "按回车键退出..."
