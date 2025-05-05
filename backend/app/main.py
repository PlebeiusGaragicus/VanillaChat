# FastAPI app entrypoint (placeholder)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VanillaChat backend is running."}

@app.get("/stream")
def stream():
    def token_generator():
        # Example simulated tokens for demonstration
        tokens = ["Hello", ",", " ", "this", " ", "is", " ", "a", " ", "streamed", " ", "response!\n"]
        for token in tokens:
            yield token
            time.sleep(0.3)  # Simulate delay between tokens
    return StreamingResponse(token_generator(), media_type="text/plain")
