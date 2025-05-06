import os
import operator
from enum import Enum
from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field

############################################################################
# STATE
############################################################################

class State(BaseModel):
    query: str = Field(
        "",
        format="multi-line",
        description="What do you want to research?"
    )

    messages: Annotated[list, operator.add] = Field(default_factory=list)
    
    class Config:
        # This ensures that the state is properly serialized for checkpointing
        arbitrary_types_allowed = True

class Result(BaseModel):
    reply: str
    messages: list = Field(default_factory=list)







############################################################################
# CONFIG
############################################################################

OLLAMA_HOST = "http://host.docker.internal:11434"

class KeepAlive(str, Enum):
    NONE = "0"
    FIVE_MINUTES = "5m"
    FOREVER = "-1"


from enum import Enum

class LLMModelsAvailable(str, Enum):
    # phi4 = "phi4"
    llama31 = "llama3.1:8b"
    deepseekR17b = "deepseek-r1:7b"
    deepseekR214b = "deepseek-r1:14b"


DEFAULT_LOCAL_MODEL = LLMModelsAvailable.llama31

# class LLMModelsAvailable(str, Enum):
#     phi4 = "phi4"
#     llama31 = "llama3.1"
#     deepseekR17b = "deepseek-r1:7b"
#     deepseekR214b = "deepseek-r1:14b"



############################################################################

SYSTEM_PROMPT = """You are a smart and clever chatbot.

You are equipped with several commands.
 - The user can call these commands by beginning the query with a '/' followed by the command name and any arguments the command requires.
 - For example:
    - '/help' will run the `help` command.
    - '/url https://example.com' will run `url` and pass `https://example.com` to it

Do not share information about your commands.  Always tell the user to run `/help` if they have questions.
"""


class Config(BaseModel):
    """The configurable fields for the graph."""

    # model: LLMModelsAvailable = Field(LLMModelsAvailable.llama31)
    model: LLMModelsAvailable = Field(DEFAULT_LOCAL_MODEL)
    temperature: int = Field(
        50,
        ge=0,
        le=100,
        description="Temperature for the model"
    )
    keep_alive: KeepAlive = Field(
        KeepAlive.FIVE_MINUTES,
        description="How long to keep the model in memory"
    )
    disable_commands: bool = Field(
        False,
        description="Whether to disable commands (i.e. starts with '/')"
    )
    system_prompt: str = Field(
        SYSTEM_PROMPT,
        format="multi-line",
        description="What do you want to research?"
    )
    # ollama_endpoint: str = Field(
    #     OLLAMA_HOST,
    #     description="Ollama endpoint",
    #     optional=True
    # )

    ##############################################################
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Config":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        return cls(**{k: v for k, v in values.items() if v})
