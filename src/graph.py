from typing import Literal

from nodes import (get_tool_nodes, 
                    model_check_query, 
                    first_tool_call,
                    model_get_schema,
                    query_gen_node,
                    SubmitFinalAnswer, 
                    State)

from langgraph.graph import START, END, StateGraph, MessagesState

workflow = StateGraph(State)

tool_node_dicts = get_tool_nodes()
list_tables_tool_node = tool_node_dicts["list_tables_tool_node"]
get_full_schema_tool_node = tool_node_dicts["get_full_schema_tool_node"]
query_db_tool_node = tool_node_dicts["query_db_tool_node"]

def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]: # type: ignore
    messages = state["messages"]
    last_message = messages[-1]
    # If there is a tool call, then we finish
    if getattr(last_message, "tool_calls", None):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"

# Define nodes
workflow.add_node("first_tool_call", first_tool_call)
workflow.add_node("list_tables_tool", list_tables_tool_node)
workflow.add_node("get_schema_tool", get_full_schema_tool_node)
workflow.add_node("model_get_schema", model_get_schema)
workflow.add_node("query_gen", query_gen_node)
workflow.add_node("correct_query", model_check_query)
workflow.add_node("execute_query", query_db_tool_node)


# Define edges
workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "model_get_schema")
workflow.add_edge("model_get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "query_gen")
workflow.add_conditional_edges(
    "query_gen",
    should_continue,
)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "query_gen")

# Compile the workflow into a runnable
app = workflow.compile()

def get_app():
    return app