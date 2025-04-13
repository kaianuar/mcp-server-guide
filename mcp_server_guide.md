# MCP Server Development Guide for AIs

This guide provides a concise overview of the Model Context Protocol (MCP) Server development process, intended for AI assistants.

## 1. Introduction: What is an MCP Server?

An MCP Server is a process that extends the capabilities of an AI/LLM client (like an IDE extension or desktop application). It acts as a bridge, allowing the AI to interact with external data sources, APIs, local filesystems, or execute specific functions.

Key Capabilities Provided by Servers:

*   **Tools:** Expose functions the AI can call (e.g., run code, query an API, fetch data).
*   **Resources:** Provide access to file-like data (e.g., file contents, database records, API responses) via URIs.
*   **Prompts:** Offer pre-defined, reusable prompt templates for specific tasks.

## 2. Core Concepts

*   **Server Instance:** The main object representing your server. Needs a unique `name` and `version`.
*   **Capabilities:** The features your server exposes. Declared during initialization. Common capabilities include:
    *   `tools`: Allows defining callable functions.
    *   `resources`: Allows providing data via URIs.
    *   `prompts`: Allows offering prompt templates.
    *   `logging`: Enables the server to send log messages to the client.
    *   `sampling`: (Client capability) Allows the *server* to request LLM generation *from the client*.
*   **Transports:** The communication mechanism between the client and server. Common types:
    *   `stdio`: Standard Input/Output. Simple, process-based communication.
    *   `sse` (Server-Sent Events): HTTP-based streaming, suitable for web contexts.

## 3. General Steps to Build an MCP Server

1.  **Choose Language/SDK:** Select an appropriate SDK (see Section 6).
2.  **Setup Environment:** Install the chosen MCP SDK and any other project dependencies.
3.  **Initialize Server:** Create an instance of the server, providing its `name`, `version`, and explicitly declaring its `capabilities`.
4.  **Define Capabilities:**
    *   **Tools:** Define a schema (name, description, input parameters with types/descriptions) and implement the handler function containing the tool's logic.
    *   **Resources:** Define metadata (URI, name, description, MIME type) and implement the read handler function.
    *   **Prompts:** Define metadata (name, description, arguments) and implement the handler function to generate prompt messages.
5.  **Choose & Configure Transport:** Select the communication transport (e.g., `stdio`).
6.  **Run the Server:** Start the server process, connecting it to the chosen transport.

## 4. Capabilities Explained

### Tools

*   **Schema:** Crucial for the AI to understand how to use the tool. Define input parameters clearly using JSON Schema or SDK-specific methods (e.g., type hints in Python, Zod in TypeScript, annotations in Java/C#).
*   **Handler:** The function that executes when the tool is called. Receives arguments based on the schema. Should return a result (often as structured text or data).
*   **Example (Conceptual Python):**
    ```python
    @mcp.tool()
    async def get_weather(latitude: float, longitude: float) -> str:
        """Gets the weather forecast.

        Args:
            latitude: The latitude.
            longitude: The longitude.
        """
        # ... implementation using an API ...
        return formatted_forecast
    ```

### Defining Tools

Tools represent actions the server can perform. They are defined with a name, an optional description, an input schema (often using libraries like Pydantic for Python or Zod for TypeScript for validation), and a handler function.

- **Name:** A unique identifier for the tool.
- **Description:** A brief explanation of what the tool does.
- **Input Schema:** Defines the expected input parameters, their types, and whether they are required or optional. This allows the MCP client (and potentially the LLM interacting with it) to understand how to use the tool correctly.
- **Handler Function:** The code that executes the tool's logic. It receives the validated input parameters and should return a dictionary containing either a `content` key (with an array of content items, usually text) or an `error` key.

**Asynchronous Operations:** Tool handlers can be asynchronous functions (using `async def` in Python or `async function` in TypeScript). This is crucial for tools that perform I/O-bound operations, such as making network requests or accessing databases, without blocking the server's main event loop. The `fetch-json` tool added to the minimal examples demonstrates this pattern, using `aiohttp` (Python) and the native `fetch` API (TypeScript) to retrieve data from a URL asynchronously.

```python
# Example Python Tool Registration (Conceptual)
from pydantic import BaseModel

### Resources

*   **URI:** The unique identifier for the resource (e.g., `file:///path/to/file`, `db://table/id`). URIs can also act as templates containing parameters (e.g., `mcp-resource://server/item/{id}`).
*   **Read Handler:** Function called when a client requests to read the resource URI. It should fetch/generate the data and return it, typically with its content type. If the URI contains parameters, the handler function typically receives the extracted values as arguments (as seen in the Python minimal example's `get_greeting_resource`).

### Prompts

*   **Templates:** Define reusable prompt structures with placeholders for arguments.
*   **Handler:** Takes arguments provided by the client and populates the template to create the final list of prompt messages.

### Sampling (Server-Side)

*   **Purpose:** Allows the *server* to leverage the *client's* LLM for generation tasks within its own logic (e.g., inside a tool handler).
*   **Check Client Capability:** *Always* check if the connected client supports sampling before attempting.
*   **Request:** Construct a `CreateMessageRequest` specifying the prompt, model preferences (hints, priorities), system prompt, max tokens, etc.
*   **Response:** Process the `CreateMessageResult` from the client.

### Logging

*   **Purpose:** Send status updates or debug information from the server to the client.
*   **Mechanism:** Use the SDK's logging notification function (often via an `exchange` or `session` object passed to handlers).
*   **Levels:** Supports standard severity levels (DEBUG, INFO, WARNING, ERROR, etc.). Clients can set a minimum level to filter messages.

## 5. Connecting a Client

*   **Configuration:** Clients (like Claude Desktop, VS Code extensions) usually require configuration to know how to launch and communicate with your server.
*   **Example (`claude_desktop_config.json`):**
    ```json
    {
      "mcpServers": {
        "enhanced-python-server": { // Must match the name used when initializing the server
          "command": "/path/to/executable/or/script/runner", // e.g., "python", "node"
          "args": [
            "/absolute/path/to/your/server/script.py", // Script/executable to run
            // ... other arguments needed by your server ...
          ],
          "cwd": "/absolute/path/to/working/directory" // Optional working directory
        }
      }
    }
    ```
*   **Key Points:** Use **absolute paths** for commands, arguments, and CWD. Ensure the `command` is executable and in the system's PATH or specified absolutely. The server name key (e.g., `enhanced-python-server`) must match the name used when initializing the server instance.
*   **See Example READMEs:** For specific `mcp-cli` commands tailored to the minimal examples, refer to the `README.md` file within each example directory (`examples/python-minimal/README.md` and `examples/typescript-minimal/README.md`).

## 6. Available SDKs

Official or community SDKs exist for various languages:

*   **Python:** [`mcp-sdk`](https://github.com/modelcontextprotocol/mcp-sdk) (Part of the main SDK repository)
*   **TypeScript/Node.js:** [`@modelcontextprotocol/sdk`](https://github.com/modelcontextprotocol/mcp-sdk) (Part of the main SDK repository)
*   **Java:** [`java-sdk`](https://github.com/modelcontextprotocol/java-sdk)
*   **Kotlin:** [`kotlin-sdk`](https://github.com/modelcontextprotocol/kotlin-sdk)
*   **C#/.NET:** [`csharp-sdk`](https://github.com/modelcontextprotocol/csharp-sdk)

Refer to the specific SDK documentation and examples for detailed usage.

## 7. Key Considerations

*   **Clear Schemas:** Define tool/prompt schemas precisely. This is how the AI understands what your server can do.
*   **Error Handling:** Implement robust error handling within your server logic and tool handlers.
*   **Security:** Be mindful of security when exposing tools that interact with filesystems, APIs, or execute commands.
*   **Transport Choice:** Use `stdio` for simple, local process communication. Use `sse` for web-based integrations.
*   **Absolute Paths:** Emphasize using absolute paths in client configurations.
*   **Debugging:** Utilize server-side logging and client-side logs (like Claude Desktop's `mcp*.log` files) for troubleshooting.

## 8. Minimal Runnable Examples

To help you get started quickly, enhanced minimal runnable server examples are provided:

*   **Python:** [./examples/python-minimal/](./examples/python-minimal/)
*   **TypeScript:** [./examples/typescript-minimal/](./examples/typescript-minimal/)

These examples demonstrate:
*   Basic server initialization with `stdio` transport and logging.
*   Definition and implementation of:
    *   A `calculate` tool (performs arithmetic).
    *   A `hello` resource (provides static text).
    *   A `summarize-text` prompt template.
*   Instructions for setup and running.
*   Example `mcp-cli` usage commands in their respective `README.md` files.

Use these as a starting point and reference for your own MCP server development.
