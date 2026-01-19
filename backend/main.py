from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from xhs_client import XHSClient
from ai_service import AIService
from contextlib import asynccontextmanager
import database  # 导入数据库模块

# 全局变量，将在 lifespan 中初始化
client = None
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    print("[*] 正在启动服务并初始化浏览器实例 (异步模式)...")
    
    # 确保数据目录存在
    import os
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"[*] 已创建数据保存目录: {data_dir}")
        
    # 初始化数据库
    database.init_db()
    print("[*] 数据库已初始化")
        
    client = XHSClient()
    await client.init()
    
    global ai_service
    ai_service = AIService()
    
    yield
    print("[*] 正在关闭服务并释放浏览器资源...")
    if client:
        await client.close()

app = FastAPI(title="小红书爆款提取工具 API", lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "XHS Extractor API is running"}

@app.post("/extract")
async def extract_content(request: ExtractRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        # 直接异步调用抓取逻辑
        result = await client.extract_note(request.url)
        
        # 保存到数据库
        if result.get("status") == "success":
            database.save_extraction(request.url, result.get("data", {}))
            
        return result
    except Exception as e:
        print(f"[CRITICAL ERROR] 后端接口崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"服务器内部错误: {str(e)}"
        }

class RecreateRequest(BaseModel):
    title: str
    content: str
    file_path: Optional[str] = None
    url: Optional[str] = None # 新增 URL 字段用于更新数据库

@app.post("/recreate")
async def recreate_content(request: RecreateRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI Service not initialized")
    
    try:
        result = await ai_service.generate_recreation(request.title, request.content, request.file_path)
        
        # 更新数据库中的 AI 结果
        if result.get("status") == "success" and request.url:
            database.update_ai_result(request.url, result.get("data", {}))
            
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/history")
async def get_history():
    """获取历史提取记录"""
    try:
        history = database.get_history()
        return {"status": "success", "data": history}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 禁用 reload 以确保单实例浏览器稳定运行
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
