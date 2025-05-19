from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

class Message(BaseModel):
    message: str

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Application server is running"}

@app.post("/echo")
async def echo(message: Message):
    return {"received": message.message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 