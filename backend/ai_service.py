import os
import logging
import json
import asyncio
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # 从环境变量获取 API Key
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        
        # 检查代理设置
        self.proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        if self.proxy:
            logger.info(f"[*] 检测到代理设置: {self.proxy}")
            # google-generativeai 使用系统环境变量，无需额外配置
        
        if not self.api_key:
            logger.warning("[!] 未检测到 GEMINI_API_KEY。请检查 .env 文件。")
        else:
            self._init_client()

    def _init_client(self):
        try:
            genai.configure(api_key=self.api_key)
            # 获取模型对象
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("[OK] Gemini AI 客户端初始化成功 (使用 google-generativeai)。")
        except Exception as e:
            logger.error(f"[!] Gemini AI 客户端初始化失败: {str(e)}")

    async def generate_recreation(self, title: str, content: str, file_path: str = None) -> Dict[str, Any]:
        """调用 Gemini 生成三种风格的二创内容"""
        
        if not self.api_key:
            return {
                "status": "error",
                "message": "未检测到 API Key。请确保在 backend/.env 文件中正确配置了 GEMINI_API_KEY。"
            }

        prompt = f"""
你是一位精通小红书流量密码的顶级博主和文案专家。
现在我给你一篇小红书笔记的原始标题和正文，请你基于这些内容进行“二创”，生成 3 种完全不同风格的爆款脚本。

---
【原始标题】：{title}
【原始正文】：{content}
---

请严格按照以下 JSON 格式输出（不要包含 markdown 代码块标识，直接返回 JSON）：

{{
    "style_a": {{
        "recreation_title": "风格A标题（高反差/颠覆观点）",
        "recreation_content": "风格A正文内容...",
        "visual_suggestion": {{
            "cover_text": "封面大字",
            "bg_description": "背景描述"
        }}
    }},
    "style_b": {{
        "recreation_title": "风格B标题（干货拆解/逻辑清晰）",
        "recreation_content": "风格B正文内容...",
        "visual_suggestion": {{
            "cover_text": "封面大字",
            "bg_description": "背景描述"
        }}
    }},
    "style_c": {{
        "recreation_title": "风格C标题（情绪共鸣/故事感）",
        "recreation_content": "风格C正文内容...",
        "visual_suggestion": {{
            "cover_text": "封面大字",
            "bg_description": "背景描述"
        }}
    }}
}}
"""

        try:
            logger.info("[*] 正在调用 Gemini API 进行二创 (设置 60s 超时)...")
            if self.proxy:
                logger.info(f"[*] 正在通过代理连接: {self.proxy}")
            
            loop = asyncio.get_event_loop()
            
            def call_gemini():
                # 使用 generate_content 方法
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                return response

            # 将超时延长至 60 秒
            response = await asyncio.wait_for(
                loop.run_in_executor(None, call_gemini),
                timeout=60.0
            )
            
            # 清理和解析 JSON
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            result = json.loads(text)
            logger.info("[OK] AI 二创内容生成成功。")
            
            # 如果提供了文件路径，将结果保存回原文件
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data['ai_recreation'] = result
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.info(f"[*] AI 二创结果已追加保存至: {file_path}")
                except Exception as e:
                    logger.error(f"[!] 保存 AI 结果到文件失败: {str(e)}")

            return {
                "status": "success",
                "data": result
            }
        except asyncio.TimeoutError:
            logger.error("[!] AI 生成超时 (60s)。请检查您的网络是否可以访问 Google 服务。")
            error_msg = "连接超时。如果您在中国大陆，请务必在 backend/.env 中配置 HTTP_PROXY (如 http://127.0.0.1:7890)。"
            return {"status": "error", "message": error_msg}
        except Exception as e:
            logger.error(f"[!] AI 二创失败: {str(e)}")
            return {
                "status": "error",
                "message": f"AI 生成失败: {str(e)}"
            }
