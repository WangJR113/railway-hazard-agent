from fastapi import FastAPI
from pydantic import BaseModel
import agent_core

app = FastAPI()

class Msg(BaseModel):
    text: str

@app.post("/chat")
def chat(msg: Msg):
    return {"reply": agent_core.chat(msg.text)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
