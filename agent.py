import asyncio
import json
import os
from dotenv import load_dotenv
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from copilotkit import CopilotKitState # extends MessagesState
from copilotkit.langgraph import copilotkit_emit_state
 
# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class Searches(TypedDict):
    query: str
    done: bool

class AgentState(CopilotKitState):
    searches: list[Searches] = []
 
class 

async def chat_node(state: AgentState, config: RunnableConfig):
    state["searches"] = [
        {"query": "Initial research", "done": False},
        {"query": "Retrieving sources", "done": False},
        {"query": "Forming an answer", "done": False},
    ]
    await copilotkit_emit_state(config, state)
 
    # Simulate state updates
    for search in state["searches"]:
        await asyncio.sleep(1)
        search["done"] = True
        await copilotkit_emit_state(config, state)
 
    # Run the model to generate a response
    response = await ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY).ainvoke([
        SystemMessage(content="You are a helpful assistant."),
        *state["messages"],
    ], config)

    print(response)