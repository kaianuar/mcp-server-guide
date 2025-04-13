# Enhanced Python Minimal MCP Server Example

This directory contains an enhanced minimal example of a Model Context Protocol (MCP) server implemented in Python using the `mcp.py` library.

## Overview

This server demonstrates key MCP features:

- **Initialization:** Sets up an MCP server named `enhanced-python-server`.
- **Tools:** Provides a `calculate` tool and an asynchronous `fetch-json` tool.
- **Resources:** Offers a static `hello` resource and a dynamic `greeting` resource.
- **Prompts:** Includes a `summarize-text` prompt template.
- **Logging:** Basic logging is integrated.

## Capabilities

- **Server Name:** `enhanced-python-server`
- **Tools:**
  - `calculate`: Performs arithmetic operations (add, subtract, multiply, divide) on two numbers (`a`, `b`) based on the `operation` argument. Returns the result as a string.
    - Arguments:
      - `a` (float, required)
      - `b` (float, required)
      - `operation` (string, optional, default: 'add', options: 'add', 'subtract', 'multiply', 'divide')
    - Returns: `string`
  - `fetch-json`: Takes a URL and asynchronously fetches JSON data, returning it as a string.
    - Arguments:
      - `url` (string): The URL to fetch JSON data from.
    - Returns: `string` (the fetched JSON data, pretty-printed) or an error message.
- **Resources:**
  - `mcp-resource://enhanced-python-server/hello`: A static resource returning a greeting message (`text/plain`).
  - `mcp-resource://enhanced-python-server/greeting/{name}`: A dynamic resource returning a personalized greeting based on the `{name}` provided in the URI (`text/plain`).
- **Prompts:**
  - `summarize-text`: A template for generating a prompt to summarize text.
    - Arguments:
      - `text_to_summarize` (string, required)

## Setup

1.  **Prerequisites:** Ensure you have Python 3.8+ and `pip` installed.
2.  **Install Dependencies:** Navigate to this directory (`examples/python-minimal`) in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

Execute the server script directly:

```bash
python server.py
```

The server will start and listen for MCP connections via standard input/output (stdio).

## Usage

Once the server is running (using `python server.py`), you can interact with it using the `mcp-cli`. Ensure you have `mcp-cli` installed (`npm install -g @modelcontextprotocol/cli`).

**Connect to the Server:**

Use the `stdio` transport to connect:

```bash
mcp connect stdio --command "python server.py"
```

Once connected, you can use the following commands in the `mcp-cli` prompt:

**1. List Capabilities:**

```
> caps
```
This will show the available tools, resources, and prompts.

**2. Use the `calculate` tool:**

```
> tool calculate --operation add --a 5 --b 3
> tool calculate --operation multiply --a 5 --b 3
```

**3. Fetch the static `hello` resource:**

```
> resource fetch mcp-resource://enhanced-python-server/hello
```

**4. Fetch the dynamic `greeting` resource:**

```
> resource fetch mcp-resource://enhanced-python-server/greeting/User
> resource fetch mcp-resource://enhanced-python-server/greeting/AI
```

**5. Use the `fetch-json` tool:**

```
# Fetch a sample todo item from JSONPlaceholder
> tool fetch-json --url https://jsonplaceholder.typicode.com/todos/1
```

**6. Use the `summarize-text` prompt:**

```
> prompt summarize-text --text_to_summarize "Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python's design philosophy emphasizes code readability with its notable use of significant whitespace."
```

**7. Disconnect:**

```
> disconnect
# or Ctrl+C
```

## Logging

The server uses Python's standard `logging` module. Informational messages (like tool calls) and errors (like division by zero) will be printed to the standard error stream where the server is running.

For detailed information on the Model Context Protocol, refer to the [official specification](https://github.com/modelcontext/specification).
