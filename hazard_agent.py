from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
import sqlite3

# ========== 阿里云DashScope配置 ==========
llm = ChatOpenAI(
    model="qwen-plus",
    api_key="sk-ws-H.YYLDLPL.q6ln.MEUCIF3qX1IKXAQNcHndza-PNoLG2CSEC4gzLtXHd2hDqkwyAiEAvkmBpg8_55AeQV8xtI1A2qIudlC-N6Iluhwhz3pJun8",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
# ========================================

def get_conn():
    conn = sqlite3.connect("hazard.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS hazard
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    status TEXT,
                    result TEXT)''')
    conn.commit()
    return conn, cur

# 工具：新增隐患记录
def add_hazard(hazard_content: str) -> str:
    """新增一条铁路隐患记录，参数hazard_content：隐患描述文字"""
    conn, cur = get_conn()
    cur.execute("INSERT INTO hazard(content, status, result) VALUES (?, ?, ?)",
                (hazard_content, "待处理", ""))
    conn.commit()
    conn.close()
    return f"✅ 隐患已登记：{hazard_content}"

# 工具：查询隐患
def query_hazard() -> str:
    """查询全部隐患台账"""
    conn, cur = get_conn()
    rows = cur.execute("SELECT * FROM hazard").fetchall()
    conn.close()
    if not rows:
        return "暂无隐患记录"
    res = ""
    for r in rows:
        res += f"编号{r[0]} | 内容:{r[1]} | 状态:{r[2]} | 处理结果:{r[3]}\n"
    return res

# 工具：标记隐患闭环
def close_hazard(hazard_id: int, handle_result: str) -> str:
    """标记隐患处理完成，hazard_id隐患编号，handle_result填写处理结果"""
    conn, cur = get_conn()
    cur.execute("UPDATE hazard SET status='已闭环', result=? WHERE id=?", (handle_result, hazard_id))
    conn.commit()
    conn.close()
    return f"✅ 编号{hazard_id}隐患已闭环，处理记录：{handle_result}"

# 绑定工具
tools = [add_hazard, query_hazard, close_hazard]
llm_with_tools = llm.bind_tools(tools)

# 大模型节点
def call_model(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 判断是否调用工具
def should_continue(state: MessagesState):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "tools"
    return END

# 搭建流程图
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")
app = workflow.compile()

# 对话入口
if __name__ == "__main__":
    print("=== 铁路隐患处置Agent（阿里云通义千问）===")
    print("可用指令示例：登记轨道松动隐患、查询隐患、把1号隐患闭环，已经加固")
    print("输入exit退出")
    while True:
        user_input = input("\n你：")
        if user_input.strip().lower() == "exit":
            break
        output = app.invoke({"messages": [("user", user_input)]})
        print("Agent：", output["messages"][-1].content)
