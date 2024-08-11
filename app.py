"""
BICO (Business Intelligence Companion)

This script implements the core functionality of BICO, a cutting-edge project that 
revolutionizes Business Intelligence (BI) workflows by seamlessly integrating 
Generative AI with complex data operations. Leveraging AWS services like Bedrock, 
Opensearch, and Quicksight, BICO transforms how BI teams construct SQL queries 
and create data visualizations.

Key components:
- Chainlit for the chat interface
- LangChain for language model interactions
- Langgraph for workflow management
- Custom tools for various functionalities (database operations, plotting, etc.)
- Integration with AWS services (Bedrock, Opensearch, Quicksight)

This application supports:
- Interactive AI conversations
- File processing and image handling
- Dynamic chart generation
- Complex BI operations including SQL query construction and data visualization

Author: Haojie Zhou
Created: August 11, 2024
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict, Annotated, List
import base64
from pathlib import Path
import chainlit as cl
import boto3
from botocore.config import Config
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable.config import RunnableConfig
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from function_tools import plot_tools, db_tools, quicksight_chaintools,search_tool
from prompts.chat_with_tools_prompt import dialogue_prompt

# Global settings
PROVIDER = ""
SEED = 1
memory = SqliteSaver.from_conn_string(":memory:")
executor = ThreadPoolExecutor()

# Define all tools used in the application
tools = [
    plot_tools.plot_chart,
    db_tools.execute_query,
    db_tools.get_table_names,
    db_tools.get_table_info,
    search_tool.match_accurate_propernoun_tool,
    db_tools.get_sql_design_guidance,
    quicksight_chaintools.get_all_datasets_from_quicksight,
    quicksight_chaintools.build_compile,
    quicksight_chaintools.create_or_operate_filter_and_control,
    quicksight_chaintools.create_or_operate_charts,
    quicksight_chaintools.create_or_select_sheet,
    quicksight_chaintools.create_or_select_quicksight_builder_with_analysis,
    quicksight_chaintools.get_analysis_info
]

tool_node = ToolNode(tools)

class AgentState(TypedDict):
    """
    Represents the state of the agent in the conversation.
    
    Attributes:
    messages (List): List of messages in the conversation.
    charts (str): JSON string representation of chart data.
    """
    messages: Annotated[list, add_messages]
    charts: str

async def setup_runnable():
    """
    Set up the runnable for the chat session.
    
    This function initializes the language model, sets up the prompt template,
    and configures the chat session.
    """
    #from langchain_anthropic import ChatAnthropic
    global PROVIDER, SEED
    bedrock_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    llm = ChatBedrock(
        model_id=bedrock_model_id,
        model_kwargs={"temperature": 0.55, "max_tokens": 200000, "top_p": 0.85}
    )
    PROVIDER, SEED = bedrock_model_id.split(".")[0], SEED + 1
    prompt = ChatPromptTemplate.from_messages([
        ("system", dialogue_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    runnable = prompt | llm.bind_tools(tools)
    cl.user_session.set("runnable", runnable)
    cl.user_session.set("messages", [])
    cl.user_session.set("charts", "")

def call_model(state: AgentState) -> AgentState:
    """
    Call the language model with the current state and return the updated state.
    
    Args:
    state (AgentState): Current state of the agent.
    
    Returns:
    AgentState: Updated state after model invocation.
    """
    try:
        messages = []
        llm = cl.user_session.get('runnable')
        for m in state["messages"][::-1]:
            messages.append(m)
            if len(messages) >= 100:
                if not hasattr(messages[-1], 'type') or messages[-1].type != "tool":
                    break
        
        response = llm.invoke(messages[::-1])
        last_message = state["messages"][-1].content if state["messages"] else ""
        charts = last_message[7:-1] if isinstance(last_message, str) and last_message.startswith("Figure(") else ""
        return {"messages": [response], "charts": charts}
    except Exception as e:
        return {"messages": [AIMessage(content=f"Error in call_model: {str(e)}. Conversation reset.")], "charts": ""}

# Define the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent", 
    lambda state: "continue" if state["messages"][-1].tool_calls else "end",
    {"continue": "action", "end": END},
)
workflow.add_edge("action", "agent")

app = workflow.compile(checkpointer=memory)

@cl.on_chat_start
async def main():
    """
    Initialize the chat session when a new conversation starts.
    """
    #boto3.client("bedrock", config=Config(retries={'max_attempts': 10}))
    await setup_runnable()

cl.on_settings_update(setup_runnable)

async def process_file(file):
    """
    Process an uploaded file and prepare it for the AI model.
    
    Args:
    file (cl.File): File object from Chainlit.
    
    Returns:
    dict: Processed file information or None if file doesn't exist.
    """
    if not Path(file.path).exists():
        return None
    
    with open(file.path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')
    
    if "image" in file.mime:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": file.mime,
                "data": file_data
            }
        }
    else:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": file.mime or "application/octet-stream",
                "data": file_data
            },
            "name": Path(file.path).stem.replace('.', '-'),
            "format": Path(file.path).suffix.lstrip('.')
        }
@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle incoming messages, process them, and generate responses.
    
    This function processes uploaded files, invokes the AI model, 
    handles chart generation, and sends the response back to the user.
    
    Args:
    message (cl.Message): Incoming message from the user.
    """
    try:
        content = [await process_file(file) for file in message.elements or []]
        content = [item for item in content if item] + [{"type": "text", "text": message.content}]
        
        response = await asyncio.get_event_loop().run_in_executor(
            executor, 
            app.invoke, 
            {"messages": [HumanMessage(content=content)]}, 
            RunnableConfig(callbacks=[cl.LangchainCallbackHandler()], recursion_limit=100, configurable={"thread_id": SEED})
        )
        
        msg = cl.Message(content="", author=f'Chatbot: {PROVIDER.capitalize()}')
        
        if response['charts']:
            try:
                import json
                import plotly.graph_objs as go
                
                figure_dict = json.loads(response['charts'].replace("'", '"'))
                figure_dict['layout']['template'] = figure_dict['layout'].get('template') or 'plotly'
                msg.elements = [cl.Plotly(name="chart", figure=go.Figure(figure_dict), display="inline")]
            except Exception as e:
                await cl.Message(content=f"Error creating chart: {str(e)}").send()
        
        await msg.stream_token(response["messages"][-1].content)
        await msg.send()
    
    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}. Please rephrase your last message.").send()
        print(f"Error in on_message: {str(e)}")
        cl.user_session.set("messages", [])
        cl.user_session.set("charts", "")
        cl.user_session.set("runnable", None)
        await setup_runnable()
        await cl.Message(content="Session reset. Please ask your question again.").send()