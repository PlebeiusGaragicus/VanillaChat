# FastAPI app entrypoint (placeholder)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VanillaChat backend is running."}
