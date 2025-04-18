from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(title="Minimax MCP Service")

# 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

class ChatRequest(BaseModel):
    messages: list
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    response: str
    usage: dict

@app.get("/")
async def read_root():
    return {"status": "healthy", "service": "minimax-mcp"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not MINIMAX_API_KEY or not MINIMAX_GROUP_ID:
        raise HTTPException(status_code=500, detail="API credentials not configured")
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "abab5.5-chat",
        "messages": request.messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MINIMAX_BASE_URL}/text/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return ChatResponse(
                response=data["choices"][0]["message"]["content"],
                usage=data["usage"]
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
