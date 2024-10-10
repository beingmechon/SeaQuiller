from typing_extensions import TypedDict
from typing import Annotated, Literal

from databasetools import DatabaseTool
from prompts import QUERY_CHECK_SYSTEM_PROMPT, QUERY_GEN_SYSTEM_PROMPT

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages.tool import ToolMessage
from langchain_openai import ChatOpenAI
# from langchain_groq.chat_models import ChatGroq

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
import json

with open('config.json', 'r') as f:
    config = json.load(f)

print(config)

llm_db = ChatOpenAI(model=config["model"], temperature=0, api_key=config["api_key"])
database_tools = DatabaseTool(llm=llm_db, 
                              db_type=config["db_type"], 
                              database=config["database"],
                              user=config["user"],
                              password=config["password"],
                              host=config["host"],
                              port=config["port"])

db_tools = database_tools.create_tools()

tools = [db_tools[tool] for tool in db_tools]

def get_tool_nodes() -> dict[str, ToolNode]:
    tools_node = ToolNode(tools)

    return {
        "tools_node": tools_node,
        "list_tables_tool_node": ToolNode([db_tools["list_tables"]]),
        "get_table_schema_tool_node": ToolNode([db_tools["get_table_schema"]]),
        "query_db_tool_node": ToolNode([db_tools["query_db"]]),
        "check_query_tool_node": ToolNode([db_tools["check_query"]]),
        "get_full_schema_tool_node": ToolNode([db_tools["get_full_schema"]]),
    }

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="The final answer to the user")

def first_tool_call(state: State) -> dict[str, list[AIMessage]]:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{
                    "name": "list_tables",
                    "args": {"input": ""},
                    "id": "tool_abcd1",
                    "type": "tool_call"
                }],
            )
        ]
    }


query_check_prompt = ChatPromptTemplate.from_messages(
    [("system", QUERY_CHECK_SYSTEM_PROMPT), ("placeholder", "{messages}")]
)

query_gen_prompt = ChatPromptTemplate.from_messages(
    [("system", QUERY_GEN_SYSTEM_PROMPT), ("placeholder", "{messages}")]
)

llm_query_check = ChatOpenAI(model=config["model"], temperature=0)
llm_query_gen = ChatOpenAI(model=config["model"], temperature=0)
llm_get_schema = ChatOpenAI(model=config["model"], temperature=0)

query_check = query_check_prompt | llm_query_check.bind_tools(tools, tool_choice="auto")
query_gen = query_gen_prompt | llm_query_gen.bind_tools([SubmitFinalAnswer])

def model_check_query(state: State) -> dict[str, list[AIMessage]]:
    return {"messages": [query_check.invoke({"messages": [state["messages"][-1]]})]}

def model_get_schema(state: State) -> dict[str, list[AIMessage]]:
    return {"messages": [llm_get_schema.invoke(state["messages"])]}

def query_gen_node(state: State):
    message = query_gen.invoke(state)

    tool_messages = []
    if message.tool_calls:
        for tc in message.tool_calls:
            if tc["name"] != "SubmitFinalAnswer":
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tc['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tc["id"],
                    )
                )
    return {"messages": [message] + tool_messages}

