# FastAPI app entrypoint (placeholder)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import Request
import json
from langchain_core.runnables import RunnableConfig
from fastapi.middleware.cors import CORSMiddleware

# Import the compiled LangGraph graph and State
from app.graphs.ollama.graph import graph
from app.graphs.ollama.state import State

app = FastAPI()

# Enable CORS for frontend port
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8080"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "VanillaChat backend is running."}

@app.post("/stream")
async def stream(request: Request):
    # Parse JSON payload with query and thread_id
    data = await request.json()
    user_query = data.get("query") or "Hello!"
    thread_id = data.get("thread_id")
    config = RunnableConfig(configurable={"thread_id": thread_id})
    state = State(query=user_query)
    # Using in-memory checkpointer; no config needed

    def serialize_custom_objects(obj):
        # Extend as needed for custom object serialization
        try:
            return obj.__dict__
        except Exception:
            return str(obj)

    def event_stream():
        # Stream only assistant outputs from the 'ollama' node
        for event in graph.stream(state, config=config):
            print("[DEBUG] Graph event:", event)
            # Expect event to be a dict mapping node name to payload
            if not isinstance(event, dict) or 'ollama' not in event:
                continue
            output = event['ollama']
            # output should be {'messages': [...]}
            try:
                data_str = json.dumps(output).replace('\n', '\\n')
                yield f"data: {data_str}\n\n"
            except Exception as e:
                print(f"Serialization error: {e}")
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
