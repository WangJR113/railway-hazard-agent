```
# 铁路隐患运维智能体
基于 Agent + FastAPI + Gradio 开发的铁路隐患问答智能体
- 后端接口：FastAPI
- Agent逻辑：agent_core.py / hazard_agent.py
- Web可视化界面：web_ui.py（Gradio）
- 数据存储：SQLite 隐患数据库

## ✨ 功能
1. 自然语言查询铁路隐患信息
2. Agent自主调用工具查询隐患库
3. 提供API接口 + 网页UI两种访问方式

## 🛠️ 启动方式
### 方式1：启动后端API
```bash
uvicorn main_api:app --reload
```
