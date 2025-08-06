import os
import json
import ast
from pymongo import MongoClient
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List

# --- Setup Phase ---
# Load environment variables from .env file
load_dotenv()

# Ensure necessary environment variables are set
mongo_uri = os.getenv("MONGO_URI")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not mongo_uri or not openai_api_key:
    raise ValueError("MONGO_URI and OPENAI_API_KEY must be set in the .env file.")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Tool Definition ---
# This is the function the LLM will learn to call.
@tool
def query_mongodb(query_dict: str, projection_dict: str = None):
    """
    Queries the 'students' collection in the 'student_records' MongoDB database.

    Args:
        query_dict (str): A string representing the Python dictionary for the find() query.
                          Example: '{"department": "Computer Science"}'
        projection_dict (str, optional): A string representing the Python dictionary for the projection.
                                          This specifies which fields to include or exclude.
                                          Example: '{"name": 1, "cgpa": 1, "_id": 0}'
                                          Defaults to None, which returns all fields.
    """
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client.student_records
        collection = db.students

        # Safely evaluate the string representation of dictionaries
        query = ast.literal_eval(query_dict) if query_dict else {}
        projection = ast.literal_eval(projection_dict) if projection_dict else None

        print(f"--- Executing MongoDB Query ---\nQuery: {query}\nProjection: {projection}\n")

        # Execute the query
        results = list(collection.find(query, projection))

        # Close the connection
        client.close()

        # If results are empty, inform the user.
        if not results:
            return "No documents found for the given query."

        # To avoid clutter, limit the number of results shown in the tool output
        if len(results) > 10:
             return f"Found {len(results)} records. Here are the first 10: {json.dumps(results[:10], indent=2)}"


        # Convert results to a JSON string to pass back to the LLM
        return json.dumps(results, indent=2)

    except Exception as e:
        # Return a formatted error message to the LLM
        return f"An error occurred: {str(e)}. Please check your query syntax. The query dictionary must be a valid Python dictionary represented as a string."

# Bind the tool to the LLM
tools = [query_mongodb]
llm_with_tools = llm.bind_tools(tools)

# --- LangGraph Agent Definition ---

# 1. Define the agent's state
class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage | ToolMessage]

# 2. Define the nodes of the graph
def call_model(state: AgentState):
    """Node that calls the LLM."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool(state: AgentState):
    """Node that executes the tool chosen by the LLM."""
    last_message = state['messages'][-1]
    # Find the tool call in the last AIMessage
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call['name']
    tool_args = tool_call['args']

    # Find the corresponding tool function
    selected_tool = None
    for t in tools:
        if t.name == tool_name:
            selected_tool = t
            break
    
    if selected_tool is None:
        raise ValueError(f"Tool '{tool_name}' not found.")

    # Execute the tool and get the result
    result = selected_tool.invoke(tool_args)
    tool_message = ToolMessage(content=str(result), tool_call_id=tool_call['id'])
    return {"messages": [tool_message]}

# 3. Define the conditional edges
def should_continue(state: AgentState):
    """Conditional edge to decide whether to continue or end."""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        # If the LLM made a tool call, we should continue to the tool node
        return "continue"
    else:
        # If the LLM did not make a tool call, we can end
        return "end"

# 4. Assemble the graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

workflow.add_edge("action", "agent")

# Compile the graph into a runnable app
app = workflow.compile()

# --- Main Interaction Loop ---
if __name__ == "__main__":
    print("AI Agent for MongoDB is running. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # Invoke the agent
        inputs = {"messages": [HumanMessage(content=user_input)]}
        response_generator = app.stream(inputs)
        
        final_response = None
        for chunk in response_generator:
            # The final response is in the 'agent' node's output
            if "agent" in chunk:
                final_response = chunk["agent"]["messages"][-1]
        
        if final_response:
            print(f"AI: {final_response.content}")
        else:
            print("AI: I'm sorry, I couldn't process that request.")