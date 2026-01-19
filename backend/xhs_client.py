import os
import asyncio
import logging
import datetime
import json
import random
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend_extraction.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class XHSClient:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        # 确保数据目录存在 (在项目根目录)
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 常用 User-Agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]

    async def init(self):
        """初始化：连接已启动的本地 Chrome"""
        # 关键修复：防止本地 CDP 连接走代理
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        
        logger.info("[*] 正在初始化浏览器连接 (CDP 模式)...")
        
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        
        print("[*] 尝试连接本地 Chrome (CDP: 9222)...")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                self._browser = await self._playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
                logger.info(f"[*] 第 {i+1} 次尝试连接成功！")
                break
            except Exception as e:
                if i < max_retries - 1:
                    logger.warning(f"[*] 连接失败 ({str(e)})，正在重试 ({i+1}/{max_retries})...")
                    await asyncio.sleep(2)
                else:
                    logger.error(f"[!] 连接本地 Chrome 失败: {str(e)}")
                    raise Exception("无法连接到 Chrome，请先运行 launch_chrome.bat！")
        
        try:
            if self._browser.contexts:
                self._context = self._browser.contexts[0]
                logger.info("[*] 成功复用本地 Chrome 上下文！")
            else:
                logger.warning("[!] 未检测到活动上下文，尝试创建新上下文...")
                self._context = await self._browser.new_context(user_agent=random.choice(self.user_agents))
            
            await self._context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"[!] 配置上下文失败: {str(e)}")
            raise e

    async def extract_note(self, url: str) -> Dict[str, Any]:
        """提取笔记内容并保存到本地"""
        if not self._context:
            await self.init()
            
        page = None
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            page = await self._context.new_page()
            # 设置随机 User-Agent
            await page.set_extra_http_headers({"User-Agent": random.choice(self.user_agents)})
            
            logger.info(f"[*] 正在访问: {url}")
            # 模拟人工延迟
            await asyncio.sleep(random.uniform(1, 2))
            
            try:
                # 对于短链接 (xhslink.com)，使用 domcontentloaded 避免 networkidle 超时
                wait_until = "domcontentloaded" if "xhslink.com" in url else "networkidle"
                await page.goto(url, wait_until=wait_until, timeout=45000)
            except Exception as e:
                logger.warning(f"[!] 页面加载超时或受阻 ({str(e)})，尝试继续提取...")
            
            # 额外等待 2 秒确保重定向完成和 JS 执行
            await asyncio.sleep(2)
            
            # 1. 检测验证码
            if await page.query_selector(".captcha-container") or "captcha" in page.url:
                logger.error("="*50)
                logger.error("[Manual Action Required] 检测到滑动验证码！")
                logger.error("[!] 请在打开的浏览器窗口中手动完成验证。")
                logger.error("="*50)
                # 等待验证码消失
                while await page.query_selector(".captcha-container") or "captcha" in page.url:
                    await asyncio.sleep(2)
                logger.info("[*] 验证码已处理，继续执行...")

            # 2. 模拟滚动，确保内容加载
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(random.uniform(1, 3))

            # 3. 深度提取逻辑 (优先使用 __INITIAL_STATE__)
            extracted_data = await page.evaluate("""() => {
                const result = {
                    title: '',
                    content: '',
                    tags: [],
                    stats: { likes: 0, collects: 0, comments: 0 },
                    author: '',
                    raw_data: null
                };

                // 优先从全局状态提取
                if (window.__INITIAL_STATE__) {
                    try {
                        const state = window.__INITIAL_STATE__;
                        const noteId = Object.keys(state.note.noteDetailMap || {})[0];
                        if (noteId) {
                            const detail = state.note.noteDetailMap[noteId].note;
                            result.title = detail.title;
                            result.content = detail.desc;
                            result.tags = detail.tagList ? detail.tagList.map(t => t.name) : [];
                            result.stats = {
                                likes: detail.interactInfo.likedCount,
                                collects: detail.interactInfo.collectedCount,
                                comments: detail.interactInfo.commentCount
                            };
                            result.author = detail.user.nickname;
                            result.raw_data = detail;
                        }
                    } catch (e) {}
                }

                // 如果状态提取失败，回退到 DOM 选择器
                if (!result.title) {
                    result.title = document.querySelector('#detail-title')?.innerText?.trim() || '';
                    result.content = document.querySelector('#detail-desc')?.innerText?.trim() || '';
                    result.author = document.querySelector('.author-name')?.innerText?.trim() || '';
                    
                    const tags = Array.from(document.querySelectorAll('a.tag, #hash-tag'));
                    result.tags = tags.map(t => t.innerText.replace('#', '').trim());
                    
                    const getStat = (sel) => parseInt(document.querySelector(sel)?.innerText?.replace(/[^0-9]/g, '') || '0');
                    result.stats = {
                        likes: getStat('.like-wrapper .count, .like-count'),
                        collects: getStat('.collect-wrapper .count, .collect-count'),
                        comments: getStat('.chat-wrapper .count, .chat-count')
                    };
                }

                return result;
            }""")

            if not extracted_data['title'] and not extracted_data['content']:
                raise Exception("抓取失败：未能提取到有效数据，请检查登录状态或页面是否被拦截。")

            # 4. 数据持久化
            note_id = url.split('/')[-1].split('?')[0]
            if not note_id or len(note_id) < 5: # 处理短链接重定向后的 ID
                note_id = timestamp
                
            file_name = f"xhs_{note_id}_{timestamp}.json"
            file_path = os.path.join(self.data_dir, file_name)
            
            save_data = {
                "url": url,
                "timestamp": datetime.datetime.now().isoformat(),
                "extracted": extracted_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"[*] 数据已完整保存至: {file_path}")

            return {
                "status": "success",
                "data": extracted_data,
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"[!] 提取异常: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
        finally:
            if page:
                await page.close()

    async def close(self):
        if self._playwright:
            await self._playwright.stop()
