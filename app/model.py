import os
import asyncio
from transformers import AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor

# Global variables for Singleton pattern
_model = None
_tokenizer = None
MODEL_NAME = os.getenv("MODEL_NAME", "distilgpt2")

# Thread pool for handling CPU-bound inference tasks
executor = ThreadPoolExecutor(max_workers=os.cpu_count())

def get_model():
    """
    Lazy loads the model and tokenizer only when needed.
    """
    global _model, _tokenizer
    if _model is None:
        print(f"Loading model {MODEL_NAME}...")
        # Added resume_download=True to help with network issues
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            resume_download=True
        )
        print("Model loaded successfully.")
    return _model, _tokenizer

def inference_task(prompt: str, max_new_tokens: int, temperature: float):
    """
    Blocking CPU-bound inference function.
    """
    model, tokenizer = get_model()
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate output
    outputs = model.generate(
        **inputs, 
        max_new_tokens=max_new_tokens, 
        temperature=temperature,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

async def generate_text(prompt: str, max_new_tokens: int, temperature: float):
    """
    Wrapper to run the blocking inference in a separate thread.
    """
    loop = asyncio.get_running_loop()
    # Run the CPU-bound inference in a thread pool to avoid blocking the async loop
    result = await loop.run_in_executor(
        executor, 
        inference_task, 
        prompt, 
        max_new_tokens, 
        temperature
    )
    return result