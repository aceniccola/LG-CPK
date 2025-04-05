import asyncio
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from copilotkit import CopilotKitState # extends MessagesState
from copilotkit.langgraph import copilotkit_emit_state
 
class Searches(TypedDict):
    query: str
    done: bool
 
class AgentState(CopilotKitState):
    searches: list[Searches] = []
 
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
    response = await ChatOpenAI(model="gpt-4o").ainvoke([
        SystemMessage(content="You are a helpful assistant."),
        *state["messages"],
    ], config)

    print(response)