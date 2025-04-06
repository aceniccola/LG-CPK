import asyncio
import os
from models import high_thinking_model, thinking_model,low_model
from tools import tools
from dotenv import load_dotenv
from typing import TypedDict, List, Dict
from langchain.agents import AgentType, initialize_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import google_cloud, BaseTool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available
)
# research hf hub tools, dappier, AINetwork, memorize (learning from exp), opengradient toolkit, oracle vectorsearch, tavily, wikipedia, human as a tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import create_react_agent
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

wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

gen_search_tool = Tool(
    name = "Google Search",
    description= "Search Google for any recent relevent results.",
    func = gen_search.run
)

class Summary(BaseModel):
    "Summary to assist in decision making"
    what: str = Field(description = "What is this argument really saying?", max_length=100)
    who: str = Field(description = "Who is the speaker and who is their likely audiance?", max_length=100)
    why: str = Field(description = "What is the likely motive behind this argument?", max_length=100)
    what_to_do: str = Field(description = "What is the most effective way to respond to this argument?", max_length=100)

class Searches(TypedDict):
    query: str
    done: bool

class AgentState(CopilotKitState):
    messages: List[Dict[str, str]]

def agent_node(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    response = high_thinking_model.ainvoke(messages)
    return {"messages": [*messages, response]}

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

def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if "action" in last_message.content.lower():
        tool_name = last_message.content.split(":")[-1].strip()
        tool_input = messages[-2].content

        if tool_name  == "search":
            tool_output = gen_search_tool.run(tool_input)
            return {"messages": [*messages, AIMessage(content=tool_output)]}
        
    return {"messages": [*messages, AIMessage(content="No action required.")]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if "action" in last_message.content.lower():
        return "use_tool"
    
    return "continue"

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tool", tool_node)

graph.set_conditional_edge("agent", should_continue, {
    "use_tool": "tool",
    "continue": END
})

graph.add_edge("tool", "agent")

app = graph.compile()

inputs = {"messages": [HumanMessage(content="What is the capital of France?")]}
result = app.invoke(inputs)
print(result)

inputs2 = {"messages": [HumanMessage(content="What is the current weather in Paris?")]}
result2 = app.invoke(inputs2)
print(result2)