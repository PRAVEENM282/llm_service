from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str = Field(..., example="Once upon a time in a digital world")
    max_new_tokens: Optional[int] = Field(50, ge=1, le=200, description="Max tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.1, le=2.0)

class GenerateResponse(BaseModel):
    generated_text: str