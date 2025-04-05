import asyncio
import json
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import google_cloud, BaseTool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from copilotkit import CopilotKitState # extends MessagesState
from copilotkit.langgraph import copilotkit_emit_state
 
# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GENERAL_SEARCH_KEY = os.getenv("GOOGLE_GENERAL_SEARCH")
gen_search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY, google_cse_id=GENERAL_SEARCH_KEY)
# Define models
high_thinking_model = ChatGoogleGenerativeAI(model="gemini-2.5-pro-preview-03-25", api_key=GOOGLE_API_KEY)
thinking_model = ChatGoogleGenerativeAI(model = "gemini-2.0-flash", api_key=GOOGLE_API_KEY)
low_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=GOOGLE_API_KEY)

gen_search_tool = Tool(
    name = "Google Search",
    description= "Search Google for any recent relevent results.",
    func = gen_search.run
)

class Summary(BaseModel):
    "Summary to assist in decision making"
    what: str = Field(description = "What is this argument really saying?")
    why: str = Field(description = "What is the likely motive behind this argument?")
    who: str = Field(description = "Who is the speaker and who is their likely audiance?")

class Searches(TypedDict):
    query: str
    done: bool

class AgentState(CopilotKitState):
    messages: List[Dict[str, str]]

def agent_node(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    response = high_thinking_model.ainvoke(messages)
    return {"messages": [*messages, response]}

def summarizer(argument: str):
    return 

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
    response = await ChatGoogleGenerativeAI(model="gemini-pro", api_key=GOOGLE_API_KEY).ainvoke([
        SystemMessage(content="You are a helpful assistant."),
        *state["messages"],
    ], config)

    print(response)