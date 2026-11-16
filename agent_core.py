import sqlite3
import re
from datetime import datetime

DB_NAME = "rail_hazard.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS hazard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pos TEXT,
        desc TEXT,
        level TEXT,
        time TEXT
    )
    ''')
    conn.commit()
    conn.close()

def parse_text(text):
    t = text.strip()
    # 查询全部
    if "查询所有隐患" in t or "查看全部" in t:
        return {"cmd": "query_all"}
    # 删除
    del_match = re.search(r"删除(\d+)号", t)
    if del_match:
        return {"cmd": "delete", "id": int(del_match.group(1))}
    # 录入隐患
    pos_match = re.search(r"(K\d+[\+\-]\d+)", t)
    level_match = re.search(r"(高|中|低)风险|等级(高|中|低)", t)
    pos = pos_match.group(1) if pos_match else "未知位置"
    level = level_match.group(1) if level_match else "中"
    desc = t
    return {"cmd": "add", "pos": pos, "desc": desc, "level": level}

def run_cmd(res):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if res["cmd"] == "add":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO hazard(pos, desc, level, time) VALUES (?,?,?,?)",
                    (res["pos"], res["desc"], res["level"], now))
        conn.commit()
        conn.close()
        return f"✅ 录入成功：位置{res['pos']}，等级{res['level']}"
    elif res["cmd"] == "query_all":
        rows = cur.execute("SELECT * FROM hazard").fetchall()
        conn.close()
        if not rows:
            return "📋 暂无隐患记录"
        out = "==== 隐患列表 ====\n"
        for r in rows:
            out += f"编号{r[0]} | 位置{r[1]} | {r[2]} | 等级{r[3]} | {r[4]}\n"
        return out
    elif res["cmd"] == "delete":
        cur.execute("DELETE FROM hazard WHERE id=?", (res["id"],))
        conn.commit()
        conn.close()
        return f"🗑️ 已删除编号 {res['id']}"
    else:
        return "❌ 无法识别指令"

def chat(text):
    init_db()
    parsed = parse_text(text)
    return run_cmd(parsed)
