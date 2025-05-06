"""This 'ollama' graph outlines a LangGraph agent with memory functionality."""

import os
from pathlib import Path
from langgraph.graph.state import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .state import State, Result, Config
graph_builder = StateGraph(State, input=State, output=Result, config_schema=Config)


## ADD ALL OUR NODES
from .nodes import ollama, _check_for_command, handle_command
graph_builder.add_node("ollama", ollama)
graph_builder.add_node("handle_command", handle_command)


## CONNECT ALL OUR NODES
graph_builder.add_conditional_edges("__start__", _check_for_command)
graph_builder.add_edge("handle_command", "__end__")
graph_builder.add_edge("ollama", "__end__")


## COMPILE AND CONFIGURE WITH PERSISTENT MEMORY
# Create an in-memory checkpointer for persistence
checkpointer = MemorySaver()

# Compile the graph with the file-based checkpointer
graph = graph_builder.compile(checkpointer=checkpointer)

# Export the checkpointer so it can be accessed from outside
# This is needed because the compiled graph doesn't expose the checkpointer directly
memory_saver = checkpointer