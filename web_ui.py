import gradio as gr
import requests

def send(text):
    r = requests.post("http://127.0.0.1:8000/chat", json={"text":text})
    return r.json()["reply"]

demo = gr.Interface(fn=send, inputs="text", outputs="text", title="铁路隐患排查助手")
demo.launch()
