# FastAPI app entrypoint (placeholder)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi import Request
import json
import uuid
from langchain_core.runnables import RunnableConfig
from fastapi.middleware.cors import CORSMiddleware

# Import the compiled LangGraph graph and State
from app.graphs.ollama.graph import graph
from app.graphs.ollama.state import State

app = FastAPI()

# Enable CORS for frontend port
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "VanillaChat backend is running."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Wait for the initial message from the client
        data = await websocket.receive_json()
        
        # Extract query and thread_id from the message
        user_query = data.get("query", "Hello!")
        thread_id = data.get("thread_id", str(uuid.uuid4()))
        
        print(f"[DEBUG] WebSocket: Processing query: '{user_query}' with thread_id: '{thread_id}'")
        
        # Create the initial state with the user's query
        state = State(query=user_query, messages=[])
        
        # Configure the graph execution
        config = RunnableConfig(
            configurable={"thread_id": thread_id}
        )
        
        # Send a start event
        await websocket.send_json({
            "type": "start",
            "message": "Starting graph execution"
        })
        
        # Stream all events from the graph using astream_events
        async for event in graph.astream_events(state, config=config, version="v1"):
            # Log the raw event
            print(f"[DEBUG] WebSocket: Raw event: {event}")
            
            try:
                # Handle dictionary events (most common format)
                if isinstance(event, dict):
                    # Check for LLM tokens in ollama messages
                    if 'ollama' in event and 'messages' in event['ollama']:
                        message = event['ollama']['messages'][0]
                        if message.get('role') == 'assistant':
                            content = message.get('content', '')
                            if content:
                                print(f"[DEBUG] WebSocket: Sending token from ollama: '{content}'")
                                await websocket.send_json({
                                    "type": "token",
                                    "content": content,
                                    "node": "ollama"
                                })
                    
                    # Check for node events
                    elif 'event' in event:
                        event_type = event['event']
                        node_name = event.get('name', 'unknown')
                        
                        # Handle node start/end events
                        if event_type.endswith('_start'):
                            print(f"[DEBUG] WebSocket: Node '{node_name}' started")
                            await websocket.send_json({
                                "type": "node_start",
                                "node": node_name
                            })
                        elif event_type.endswith('_end'):
                            print(f"[DEBUG] WebSocket: Node '{node_name}' completed")
                            # Try to extract output data
                            output = event.get('data', {}).get('output')
                            await websocket.send_json({
                                "type": "node_end",
                                "node": node_name,
                                "output": output
                            })
                        # Handle LLM token streaming
                        elif event_type == 'on_chat_model_stream':
                            # Extract token from chunk if available
                            data = event.get('data', {})
                            if 'chunk' in data and hasattr(data['chunk'], 'content'):
                                token = data['chunk'].content
                                if token:
                                    print(f"[DEBUG] WebSocket: Sending LLM token: '{token}'")
                                    await websocket.send_json({
                                        "type": "token",
                                        "content": token,
                                        "node": node_name
                                    })
                # Handle object-based events
                elif hasattr(event, 'event'):
                    event_type = event.event
                    node_name = getattr(event, 'name', 'unknown')
                    
                    # Handle LLM token streaming
                    if event_type == 'on_chat_model_stream':
                        if hasattr(event.data, 'chunk') and hasattr(event.data.chunk, 'content'):
                            token = event.data.chunk.content
                            if token:
                                print(f"[DEBUG] WebSocket: Sending LLM token from object: '{token}'")
                                await websocket.send_json({
                                    "type": "token",
                                    "content": token,
                                    "node": node_name
                                })
                    # Handle other event types
                    elif event_type.endswith('_start'):
                        print(f"[DEBUG] WebSocket: Node '{node_name}' started (object)")
                        await websocket.send_json({
                            "type": "node_start",
                            "node": node_name
                        })
                    elif event_type.endswith('_end'):
                        print(f"[DEBUG] WebSocket: Node '{node_name}' completed (object)")
                        await websocket.send_json({
                            "type": "node_end",
                            "node": node_name,
                            "output": str(getattr(event.data, 'output', None))
                        })
                # Handle any other event types
                else:
                    print(f"[DEBUG] WebSocket: Unknown event type: {type(event)}")
                    await websocket.send_json({
                        "type": "event",
                        "data": str(event)
                    })
            except Exception as e:
                print(f"[ERROR] WebSocket: Error processing event: {e}")
        
        # Send a completion event
        await websocket.send_json({"type": "complete"})
        
    except WebSocketDisconnect:
        print(f"[DEBUG] WebSocket: Client disconnected")
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        # Try to send an error message if the connection is still open
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

@app.get("/stream")
@app.post("/stream")
async def stream(request: Request):
    # Handle both GET and POST requests
    if request.method == "GET":
        # Parse query parameters
        params = request.query_params
        user_query = params.get("query") or "Hello!"
        thread_id = params.get("thread_id") or str(uuid.uuid4())
    else:  # POST
        # Parse JSON payload
        data = await request.json()
        user_query = data.get("query") or "Hello!"
        thread_id = data.get("thread_id") or str(uuid.uuid4())
    
    print(f"[DEBUG] Processing request with query: '{user_query}' and thread_id: '{thread_id}'")
    
    # Create the initial state with the user's query
    state = State(query=user_query, messages=[])
    
    # Configure the graph execution
    config = RunnableConfig(
        configurable={"thread_id": thread_id}
    )
    
    def serialize_custom_objects(obj):
        """Convert custom objects to serializable format"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        return str(obj)

    async def event_stream():
        """Generate a stream of events from the graph"""
        print(f"[DEBUG] Starting stream with thread_id: {thread_id}")
        
        try:
            # Use astream for async streaming
            async for event in graph.stream(state, config=config):
                print(f"[DEBUG] Raw event: {event}")
                
                if 'ollama' in event:
                    # Extract the message content
                    if 'messages' in event['ollama'] and event['ollama']['messages']:
                        message = event['ollama']['messages'][0]
                        if message.get('role') == 'assistant':
                            # Serialize the event for SSE
                            try:
                                serialized_event = json.dumps(
                                    {"chunk": event}, 
                                    default=serialize_custom_objects
                                ).replace('\n', '\\n')
                                
                                print(f"[DEBUG] Sending chunk: {serialized_event[:100]}...")
                                yield f"data: {serialized_event}\n\n"
                            except Exception as e:
                                print(f"[ERROR] Serialization error: {e}")
            
            # Send a completion event
            yield "event: complete\ndata: {}\n\n"
            
        except Exception as e:
            print(f"[ERROR] Stream error: {e}")
            error_data = json.dumps({"error": str(e)}, default=serialize_custom_objects).replace('\n', '\\n')
            yield f"data: {error_data}\n\n"
    
    # Return a streaming response
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "text/event-stream"
        }
    )
