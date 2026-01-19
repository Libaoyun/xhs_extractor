import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "history.db")

def init_db():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            content TEXT,
            images TEXT, -- JSON array of image URLs
            ai_result TEXT, -- JSON object of AI recreation
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_extraction(url: str, data: Dict[str, Any]) -> int:
    """保存提取结果，返回记录 ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 简单的去重逻辑：如果 URL 已存在，则更新
    c.execute("SELECT id FROM history WHERE url = ?", (url,))
    existing = c.fetchone()
    
    images_json = json.dumps(data.get("images", []), ensure_ascii=False)
    created_at = datetime.now().isoformat()
    
    if existing:
        record_id = existing[0]
        c.execute('''
            UPDATE history 
            SET title = ?, content = ?, images = ?, created_at = ?
            WHERE id = ?
        ''', (data.get("title"), data.get("content"), images_json, created_at, record_id))
    else:
        c.execute('''
            INSERT INTO history (url, title, content, images, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, data.get("title"), data.get("content"), images_json, created_at))
        record_id = c.lastrowid
        
    conn.commit()
    conn.close()
    return record_id

def update_ai_result(url: str, ai_result: Dict[str, Any]):
    """更新 AI 二创结果"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ai_json = json.dumps(ai_result, ensure_ascii=False)
    c.execute("UPDATE history SET ai_result = ? WHERE url = ?", (ai_json, url))
    conn.commit()
    conn.close()

def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    """获取历史记录"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    
    history = []
    for row in rows:
        item = dict(row)
        # 解析 JSON 字段
        try:
            item['images'] = json.loads(item['images']) if item['images'] else []
            item['ai_result'] = json.loads(item['ai_result']) if item['ai_result'] else None
        except:
            pass
        history.append(item)
        
    conn.close()
    return history

# 初始化数据库
init_db()
