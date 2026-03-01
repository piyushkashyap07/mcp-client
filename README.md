# LangGraph FastMCP Client (Calculator)

This directory contains a client for the Model Context Protocol (MCP) using `langchain-mcp-adapters` and `langgraph`. It demonstrates how a Large Language Model (in this case, OpenAI's `gpt-4o-mini`) can connect to a remote MCP server, automatically discover available tools (like `add`, `subtract`, `multiply`, `divide`), and leverage a LangGraph agent to intelligently orchestrate and invoke those tools to solve math problems.

## Architecture

- **Client**: A Python script (`client.py`) that acts as a LangGraph agent. It communicates over `streamable-http`.
- **Server**: A fastMCP server (running locally on port `8000` by default) that provides calculator operations. The client does *not* contain any of the math logic itself.

## Setup

1. Make sure you have an active `.env` file in this directory containing your OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

2. Activate your Python environment or use `uv` for dependency management. If using `uv`, no standard `pip install` is necessary, just use the `uv run` command.

## Running the Architecture

To run the whole system, you need the MCP server running *before* starting the client.

1. **Start the MCP Server** (in a separate terminal where your Server code lives):
   ```bash
   python server.py
   ```
   *(Ensure the server binds to `127.0.0.1:8000` to match the client's configuration.)*

2. **Run the Client** (in this directory):
   ```bash
   uv run client.py
   ```

## What it Demonstrates

When you run the client, it will print out the following events:
1. **Tool Discovery**: Connecting to the MCP Server and dynamically fetching the tool schema definitions.
2. **Graph Execution**: The `gpt` model evaluating the prompt `"what's (3 + 5) x 12?"`
3. **Tool Invocation**: The LLM passing arguments back to the MCP server securely (e.g., `add({'numbers': [3, 5]})`).
4. **Final Answer**: Synthesizing the results returned by the MCP Server into a human-readable string.
