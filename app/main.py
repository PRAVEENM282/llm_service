import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.schemas import GenerateRequest, GenerateResponse
from app.model import generate_text

app = FastAPI(title="LLM Serving API", version="1.0.0")

# Security Configuration
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "mysecurekey123")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validates the API Key from the header."""
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")
 
@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "ok", "message": "Service is running"}

@app.post("/generate", response_model=GenerateResponse)
async def generate(
    payload: GenerateRequest, 
    api_key: str = Depends(get_api_key)
):
    """
    Generates text based on prompts.
    Handles concurrency by offloading to a thread pool.
    """
    try:
        result = await generate_text(
            payload.prompt, 
            payload.max_new_tokens, 
            payload.temperature
        )
        return GenerateResponse(generated_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))