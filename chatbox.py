# chatbox.py
import requests

API_URL = "http://127.0.0.1:8000/chat"

def main():
    print("===== 铁路隐患排查助手（终端版）=====")
    print("输入指令，输入 exit 退出\n")
    while True:
        text = input("你：")
        if text.strip().lower() == "exit":
            print("退出")
            break
        try:
            resp = requests.post(API_URL, json={"text": text})
            if resp.status_code == 200:
                res = resp.json()
                print(f"助手：{res['reply']}\n")
            else:
                print(f"助手：接口错误，状态码 {resp.status_code}\n")
        except Exception as e:
            print(f"助手：请求失败：{str(e)}\n")

if __name__ == "__main__":
    main()
