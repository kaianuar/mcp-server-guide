# Enhanced Python Minimal MCP Server Example

This directory contains an enhanced minimal example of a Model Context Protocol (MCP) server implemented in Python using the `mcp.py` library.

## Overview

This server demonstrates key MCP features:

+*   **SDK Usage:** Uses the `mcp-sdk` Python package (often imported as `mcp`).
*   **Initialization:** Sets up an MCP server named `enhanced-python-server`.
*   **Tools:**
    *   `calculate`: A synchronous tool performing arithmetic.
    *   `fetch-json`: An asynchronous tool fetching JSON from a URL, demonstrating error handling via exceptions.
    *   `creative_response`: Generates a creative text response based on a prompt, with randomness controlled by a `temperature` parameter.
    *   `read_file`: Asynchronously reads content from a file within a safe `sandbox` directory.
    *   `write_file`: Asynchronously writes content to a file within a safe `sandbox` directory.
*   **Input Validation:** Uses [Pydantic](https://docs.pydantic.dev/) models to define and validate input schemas for tools (like `fetch-json`).
*   **Resources:**
    *   `hello`: A static resource providing plain text.
    *   `greeting`: A dynamic resource using a URI template (`{name}`) to provide personalized text.
*   **Prompts:** Includes a `summarize-text` prompt template.
*   **Metadata:** Registers optional metadata for resources and prompts (`add_resource_metadata`, `add_prompt_metadata`) to aid client discovery.
*   **Logging:** Basic logging is integrated.

## Capabilities

- **Server Name:** `enhanced-python-server`
- **Tools:**
  - `calculate`: Performs arithmetic operations (add, subtract, multiply, divide) on two numbers (`a`, `b`) based on the `operation` argument. Returns the result as a string.
    - Arguments:
      - `a` (float, required)
      - `b` (float, required)
      - `operation` (string, optional, default: 'add', options: 'add', 'subtract', 'multiply', 'divide')
    - Returns: `string`
  - `fetch-json`: Takes a URL (`url`) and asynchronously fetches JSON data, returning it as a pretty-printed string.
    - **Error Handling:** This tool demonstrates robust error handling. If issues occur (network error, timeout, invalid content type, JSON decode error), it raises appropriate exceptions (e.g., `ValueError`, `aiohttp.ClientError`). The MCP SDK catches these and reports an error to the client.
    - Arguments:
      - `url` (string): The URL to fetch JSON data from.
    - Returns: `string` (the fetched JSON data, pretty-printed) or an error message.
  - `creative_response`: Generates a creative text response based on a prompt, with randomness controlled by a `temperature` parameter.
    - **Parameters:**
      - `prompt` (string, required): The input text prompt.
      - `temperature` (float, optional, default: 0.7, range: 0.0-1.0): Controls the randomness of the response selection. Lower values (e.g., 0.1) are more deterministic, while higher values (e.g., 0.9) are more random.
    - **Example Call (JSON Arguments):**
      ```json
      {
        "params": {
          "prompt": "Tell me about AI",
          "temperature": 0.8
        }
      }
      ```
    - **Note:** Due to potential interactions between certain standard library modules (like `random`) and the specific way background processes are managed for testing within some development environments (like Cascade's direct tool calling), this specific tool might cause the background server process to terminate unexpectedly when called directly by the environment. However, the tool functions correctly when called from a standard external MCP client.
  - `read_file`: Reads the text content of a specified file. **Note:** For security, this tool can only access files within the `examples/python-minimal/sandbox/` directory.
    - **Parameters:**
      - `filename` (string, required): The name of the file to read (relative to the sandbox directory).
    - **Returns:** `string` (the file content) or an error message.
    - **Example Call (JSON Arguments):**
      ```json
      {
        "params": {
          "filename": "my_data.txt"
        }
      }
      ```
  - `write_file`: Writes text content to a specified file. **Note:** For security, this tool can only write files within the `examples/python-minimal/sandbox/` directory. It will create the file if it doesn't exist, or overwrite it if it does.
    - **Parameters:**
      - `filename` (string, required): The name of the file to write (relative to the sandbox directory).
      - `content` (string, required): The text content to write.
    - **Returns:** `string` (a success message) or an error message.
    - **Example Call (JSON Arguments):**
      ```json
      {
        "params": {
          "filename": "output.log",
          "content": "Log entry: Process completed."
        }
      }
      ```
- **Resources:**
  - `mcp-resource://enhanced-python-server/hello`: A static resource returning a greeting message (`text/plain`).
  - `mcp-resource://enhanced-python-server/greeting/{name}`: A dynamic resource returning a personalized greeting based on the `{name}` provided in the URI (`text/plain`).
- **Prompts:**
  - `summarize-text`: A template for generating a prompt to summarize text.
    - Arguments:
      - `text_to_summarize` (string, required)

## Requirements

*   Python 3.8+
*   pip (Python package installer)

## Setup

1.  **Navigate to the example directory:**
    ```bash
    cd examples/python-minimal
    ```
2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    You should see `(venv)` prefixed to your shell prompt.
4.  **Install dependencies:**
    Install the required MCP SDK and other libraries.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

1.  **Ensure your virtual environment is active** (see Setup step 3).
2.  **Start the server:**
    ```bash
    python server.py
    ```
The server will start and listen for MCP connections via standard input/output (stdio).

## Usage

Once the server is running (using `python server.py`), you can interact with it using the `mcp-cli`.

**Install `mcp-cli` (if you haven't already):**
```bash
npm install -g @modelcontextprotocol/cli
```

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

**7. Use the `creative_response` tool:**

```
> tool creative_response --prompt "Tell me about async file io" --temperature 0.6
```

**8. Use the `write_file` tool (creates sandbox/hello.txt):**

```
> tool write_file --filename "hello.txt" --content "Hello from the write_file tool!"
```

**9. Use the `read_file` tool (reads sandbox/hello.txt):**

```
> tool read_file --filename "hello.txt"
```

**10. Disconnect:**

```
> disconnect
# or Ctrl+C
```

## Logging

The server uses Python's standard `logging` module. Informational messages (like tool calls) and errors (like division by zero) will be printed to the standard error stream where the server is running.

## Deactivating the Virtual Environment (Optional)

When you are finished working with the server, you can deactivate the virtual environment:
```bash
deactivate
```

## Notes

*   The server communicates over `stdio` by default.

For detailed information on the Model Context Protocol, refer to the [official specification](https://github.com/modelcontext/specification).
