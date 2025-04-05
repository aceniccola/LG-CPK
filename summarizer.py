from langchain.pydantic_v1 import BaseModel, Field

class Summary(BaseModel):
    "Summary to assist in decision making"
    what: str = Field(description = "What is this argument really saying?")
    why: str = Field(description = "What is the likely motive behind this argument?")
    who: str = Field(description = "Who is the speaker and who is their likely audiance?")

def summarizer(argument: str):
    return 
