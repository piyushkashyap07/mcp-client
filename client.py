import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

async def main():
    
    # Get keys from environment variables
    openai_key = os.getenv("OPENAI_API_KEY")

    # Initialize the model
    model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
    
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8000/mcp"  
            }
        }
    )    
    
    
    
    tools = await client.get_tools()
    
    # Let's print the tools we just fetched from the MCP server!
    print("--- Connected to MCP server! ---")
    print("Available tools from MCP:")
    for t in tools:
        print(f" - {t.name}: {t.description}")
        
    model_with_tools = model.bind_tools(tools)
    print(model_with_tools)
    
    tool_node = ToolNode(tools)
    
    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
        
        
        
    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}
        
        
    builder = StateGraph(MessagesState)
    
    builder.add_node("call_model", call_model)
    
    builder.add_node("tools", tool_node)
    
    
    builder.add_edge(START, "call_model")
    
    builder.add_conditional_edges(
        "call_model",
        should_continue,
    )
    builder.add_edge("tools", "call_model")
    
    
    
    # Compile the graph
    graph = builder.compile()

    # running the graph
    print("\n--- Running LangGraph execution ---")
    question = "what's (3 + 5) x 12?"
    print(f"Question: {question}\n")
    
    async for event in graph.astream({"messages": question}):
        for node, values in event.items():
            print(f"Execution step from node: '{node}'")
            messages = values.get("messages", [])
            if not messages:
                continue
            last_msg = messages[-1]
            
            # Check if the AI called a tool
            if getattr(last_msg, "tool_calls", None):
                for tool_call in last_msg.tool_calls:
                    print(f"  -> AI called tool: {tool_call['name']}({tool_call['args']})")
                    
            # Check if the node is a tool returning output
            elif last_msg.type == "tool":
                print(f"  -> Tool '{last_msg.name}' returned output: {last_msg.content}")

    print(f"\nFinal Answer: {event[node]['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())
