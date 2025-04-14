# Guide to Building Model Context Protocol (MCP) Servers

## Introduction

The Model Context Protocol (MCP) provides a standardized way for Large Language Model (LLM) applications (clients) to interact with external data sources and functionalities (servers). Think of it as a specialized API layer designed specifically for AI interactions.

**Core Interaction Flow:**

```
+ +---------------------+        MCP / JSON-RPC        +---------------------+      +--------------------+
+ |                     | <--------------------------> |                     | ---> | External Data/Tool |
+ |   LLM Application   |                              |     MCP Server      |      | (Database, API, etc)|
+ |      (Client)       |                              |   (Your Code Here)  | <--- |                    |
+ |                     |                              |                     |      +--------------------+
+ +---------------------+                              +---------------------+
+           |
+           | 1. Client connects & discovers capabilities (Tools, Resources, Prompts)
+           |    (e.g., via stdio, SSE)
+           |
+           | 2. Client sends request (e.g., callTool, readResource)
+           |-------------------------------------------->|
+           |
+           | 3. Server handler executes, potentially interacts with External Data/Tool
+           |
+           | 4. Server sends response (tool output, resource content, error)
+           |<--------------------------------------------|
+           |
+           | (...repeat steps 2-4...)
+
```

This guide explains how to build the **MCP Server** component using the official TypeScript and Python SDKs.

## Getting Started

### 1. Install the SDK

First, you need to install the appropriate SDK for your chosen language:

*   **TypeScript:**
    ```bash
    npm install @modelcontextprotocol/sdk zod zod-to-json-schema
    # or
    yarn add @modelcontextprotocol/sdk zod zod-to-json-schema
    ```
*   **Python:**
    It's strongly recommended to use a virtual environment (`venv`).
    ```bash
    # In your project directory (e.g., examples/python-minimal)
    python3 -m venv venv      # Create venv
    source venv/bin/activate  # Activate (Linux/macOS)
    # .\venv\Scripts\activate  # Activate (Windows)

    # Install dependencies from requirements.txt
    pip install -r examples/python-minimal/requirements.txt
    ```
    The `requirements.txt` file should typically include `mcp-sdk`, `pydantic`, and any other necessary libraries like `aiohttp`.

### 2. Basic Server Setup

The SDKs provide `FastMCP`, a high-level, decorator-based class (inspired by frameworks like FastAPI) for easily defining server capabilities. It's the recommended starting point for both languages.

*   **TypeScript (`server.ts`):**
    ```typescript
    import { FastMCP } from "@modelcontextprotocol/sdk/server/fast_mcp/index.js";
    import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
    import { z } from "zod"; // Often needed for schemas

    const mcp = new FastMCP(
      "my-cool-ts-mcp-server", // Server name
      // "1.0.0" // Optional version
      // No explicit capabilities dict needed with FastMCP decorators
    );

    console.error(`MCP Server '${mcp.name}' initialized.`); // Use mcp.name

    // ... Define Tools, Resources, Prompts using @mcp decorators here ...

    async function main() {
      console.error("Starting server via stdio...");
      const transport = new StdioServerTransport();
      // FastMCP handles the connection internally via run()
      await mcp.run(transport);
      console.error("Server connected.");
    }

    // Only start if not running in a test environment
    if (process.env.NODE_ENV !== 'test') {
      main().catch(err => {
        console.error("Server failed to start:", err);
        process.exit(1);
      });
    }
    ```

*   **Python (`server.py`):**
    ```python
    import asyncio
    import logging
    import sys
    from pydantic import BaseModel # Often needed for schemas
    from mcp_sdk import FastMCP # Use FastMCP for the high-level interface

    # Configure logging (adjust level and format as needed)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    # Instantiate the server
    mcp = FastMCP(
      "my-cool-py-mcp-server", # Server name (use mcp.name to access)
      # version="1.0.0", # Optional version
      # No explicit capabilities dict needed with FastMCP decorators
    )

    log.info(f"MCP Server '{mcp.name}' initialized.") # Use mcp.name

    # ... Define Tools, Resources, Prompts using @mcp decorators here ...

    if __name__ == "__main__":
        # Ensure correct asyncio policy on Windows if needed
        if sys.platform == "win32" and sys.version_info >= (3, 8):
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        log.info("Preparing to run MCP server...")
        log.info(f"Starting MCP server '{mcp.name}' via mcp.run()...")
        try:
            mcp.run() # Handles stdio transport and blocks until client disconnects
            log.info(f"MCP server '{mcp.name}' finished running.")
        except KeyboardInterrupt:
            log.info("Server stopped by user (KeyboardInterrupt).")
        except Exception as e:
            log.error(f"MCP server encountered an unexpected error during run.", exc_info=True)
        finally:
             log.info("Server process exiting.")
    ```

### 3. Schemas for Inputs (Zod / Pydantic)

MCP relies on JSON Schema to define the expected structure of inputs for Tools and Prompts. The SDKs integrate well with popular validation libraries:

*   **[Zod](https://zod.dev/) (TypeScript):** Used to define input objects and automatically generate JSON Schema.
*   **[Pydantic](https://docs.pydantic.dev/) (Python):** Used to define input models and automatically generate JSON Schema.

You'll see these used extensively in the examples to ensure data passed to your handlers is correctly structured and typed.

## Defining Tools

Tools represent actions or functions the server can perform when requested by the client.

**Error Handling in Tools:**

If a tool encounters an error during execution (e.g., failed network request, invalid calculation), it should **throw an Error** (or a custom subclass of Error).

**Why Throw?** The MCP SDK's server framework includes built-in error handling. When you throw an error from your handler, the SDK catches it and automatically formats it into the standard JSON-RPC error response structure required by the MCP protocol before sending it back to the client. This is simpler and more consistent than manually constructing error objects.

*   **TypeScript (`FastMCP` Decorator):**
    Use the `@mcp.tool()` decorator. The schema is derived from Zod objects.
    ```typescript
    import { z } from "zod";

    // Define input schema using Zod
    const EchoParamsSchema = z.object({
      message: z.string(),
    });

    @mcp.tool({
      name: "echo", // Optional: defaults to method name
      description: "Simply returns the message provided.",
      inputSchema: EchoParamsSchema,
      // outputSchema: z.string() // Optional: if output needs validation
    })
    async echo(params: z.infer<typeof EchoParamsSchema>): Promise<string> {
      console.error(`Executing echo with message: '${params.message}'`);
      if (!params.message) {
          // Example: Throwing an error for invalid input
          throw new Error("Message cannot be empty");
      }
      return params.message;
    }
    ```

*   **Python (`FastMCP` Decorator):**
    Use the `@mcp.tool()` decorator. The schema is inferred from Pydantic type hints.
    ```python
    from pydantic import BaseModel

    # Define input schema using Pydantic
    class EchoParams(BaseModel):
        message: str

    @mcp.tool() # name defaults to function name 'echo'
    async def echo(params: EchoParams) -> str:
        """Simply returns the message provided."""
        log.info(f"Executing echo with message: '{params.message}'")
        if not params.message:
            # Example: Throwing an error for invalid input
            raise ValueError("Message cannot be empty")
        return params.message

    # Example for a tool with specific name/description
    class FetchJsonParams(BaseModel):
        url: str

    @mcp.tool(
        name="fetch-json",
        description="Fetches JSON data from a given URL."
        # No 'input_schema' argument needed, inferred from 'params: FetchJsonParams'
    )
    async def fetch_json(params: FetchJsonParams) -> str:
         """Fetches JSON data asynchronously."""
         # ... implementation using aiohttp ...
         log.info(f"Executing fetch_json for URL: {params.url}")
         # ... rest of async implementation ...
         return json_string # Return JSON as a string
    ```
    The decorator automatically handles registration and uses the Pydantic model (`EchoParams`, `FetchJsonParams`) for input validation and schema generation. Notice that the `input_schema` parameter is *not* passed to the decorator; it's inferred from the type hint.

### Example: Sampling with Temperature (Python)

You can introduce parameters to control the behavior of your tools, such as a `temperature` for sampling-based generation.

```python
# (from examples/python-minimal/server.py)
import random
from pydantic import BaseModel, Field
import logging

# ... (assuming 'mcp' FastMCP instance and 'log' logger are defined)

class CreativeResponseParams(BaseModel):
    prompt: str = Field(..., description="The input prompt for the creative response.")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Controls randomness. Lower values are more deterministic, higher values are more random."
    )

@mcp.tool(
    name="creative_response",
    description="Generates a creative response based on a prompt, influenced by temperature.",
)
async def creative_response_tool(params: CreativeResponseParams) -> str:
    log.info(f"Tool 'creative_response' called with prompt: '{params.prompt}', temperature: {params.temperature}")
    responses = [
        f"A very straightforward answer about: {params.prompt}",
        f"Thinking outside the box regarding: {params.prompt}",
        f"A whimsical take on: {params.prompt}",
        f"Let's get abstract with: {params.prompt}"
    ]
    if params.temperature < 0.3:
        chosen_response = responses[0]
    elif params.temperature > 0.8:
        chosen_response = random.choice(responses)
    else:
        chosen_response = random.choice(responses[:2])
    log.info(f"Tool 'creative_response' completed. Response: '{chosen_response}'")
    return chosen_response
```

**Calling the Tool:** The arguments should be nested under a `"params"` key:

```json
{
  "params": {
    "prompt": "Some creative prompt",
    "temperature": 0.6
  }
}
```

**Important Testing Note:** Due to potential interactions between certain standard library modules (like `random`) and the specific way background processes are managed for testing within some development environments (like Cascade's direct tool calling), tools like this might cause the background server process to terminate unexpectedly when called directly by the environment. However, they should function correctly when called from a standard external MCP client.

## Defining Resources

Resources expose data to the client. They are identified by URIs.

**Resource URI Schemes:** You can define your own URI schemes (e.g., `database://`, `my-api://`, `system://`). Choose schemes that are descriptive and make sense for your server's context. The client will use these exact URIs to request resources.

### Static Resources

Static resources provide fixed data identified by a specific URI. They don't take parameters from the URI path itself.

*   **Python (`@mcp.resource` decorator):** Define an async function that returns `ResourceContents`.

    ```python
    # examples/python-minimal/server.py
    from mcp_sdk import ResourceContents
    import logging

    # ... (assuming 'mcp' FastMCP instance and 'log' logger are defined)

    @mcp.resource(uri="mcp-resource://enhanced-python-server/hello")
    async def hello_resource() -> ResourceContents:
        """A simple static resource handler."""
        log.info("Static resource '/hello' requested.")
        return ResourceContents(
            uri="mcp-resource://enhanced-python-server/hello",
            content_type="text/plain",
            content="Hello from the enhanced Python MCP server!"
        )
    ```

*   **TypeScript (`@mcp.resource` decorator):** Define an async method that returns `Promise<ResourceContents>`.

    ```typescript
    // examples/typescript-minimal/src/server.ts
    import { ResourceContents } from "@modelcontextprotocol/sdk";
    import { logInfo } from "./utils"; // Assuming a logging utility

    // ... (within the server class definition where 'mcp' is an instance of FastMCP)

    @mcp.resource({
      uri: "mcp-resource://enhanced-typescript-server/hello",
      description: "A simple static resource.",
      // No schema needed for static resources without parameters
    })
    async helloResource(
      uri: string,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      handlerArgs: any // See note below about handlerArgs type
    ): Promise<ResourceContents> { // Use ResourceContents type here
      logInfo(`Static resource '${uri}' requested.`);
      return {
        uri: uri,
        content_type: "text/plain",
        content: "Hello from the enhanced TypeScript MCP server!",
      };
    }
    ```

### Dynamic Resources (Templates)

**TypeScript Handler Signature Note:**

Currently, the TypeScript SDK's type definitions (`ReadResourceTemplateCallback`) do not seem to automatically infer the types of parameters defined in the `ResourceTemplate` (e.g., `{name}`) into the second argument (`variables`). This means a signature like `async (uri, { name }) => { ... }` will likely cause a TypeScript error.

The recommended workaround is to type the second argument as `any` and manually extract/validate the parameters within the handler function. **Be cautious when accessing properties on `handlerArgs: any`**, as they lack compile-time checks. Consider adding runtime checks or type guards if necessary for robustness.

**Note on Resource Handler Return Types (TypeScript):**

Due to potential type mismatches encountered with `@modelcontextprotocol/sdk@1.8.0`, the return type for resource handlers in the example (`hello-resource` and the `greetingHandler` template) has been temporarily set to `Promise<any>`. This bypasses strict TypeScript checking to allow the server to run correctly. This should ideally be revisited if clearer type definitions or examples become available for this SDK version.

## Running the Server

MCP servers typically communicate with clients over standard input/output (stdio) using a JSON-RPC protocol. The SDKs provide `StdioServerTransport` to handle this.

To run your server, execute your main script (`server.ts` compiled to `.js`, or `server.py`) from the command line:

*   **TypeScript (after compiling):**
    ```bash
    # Assuming server.ts is compiled to dist/server.js
    node dist/server.js --stdio
    ```
    *(Note: The `--stdio` flag isn't strictly required by the SDK transport itself, but often used by clients like Cursor to identify how to connect.)*

*   **Python:**
    ```bash
    python server.py --stdio
    ```

**Important:** When using stdio transport:
*   **Server logs (debugging, info, errors) MUST be written to `stderr`.**
*   **`stdout` is strictly reserved for the JSON-RPC messages** exchanged with the client. Using `console.log` (TS) or `print` without `file=sys.stderr` (Python) for general logging will break the communication.

## Client Interaction (Briefly)

Clients interact with the server using an MCP client library. They typically:
1.  Connect to the running server (often via stdio).
2.  Discover available tools, resources, and prompts.
3.  Make requests (e.g., `callTool`, `readResource`).
4.  Receive responses (tool output, resource content, errors).

Details of client implementation are outside the scope of this server guide.

## Next Steps

Explore the `examples/` directory within this repository for fully runnable Python and TypeScript servers demonstrating these concepts. Each example includes its own README with specific setup and usage instructions.
