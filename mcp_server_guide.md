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
    ```bash
    pip install mcp-sdk pydantic
    ```

### 2. Basic Server Setup

Every MCP server starts by instantiating the `Server` class:

*   **TypeScript (`server.ts`):**
    ```typescript
    import { Server } from "@modelcontextprotocol/sdk/server/index.js";
    // Required for stdio communication
    import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

    const server = new Server(
      {
        // Server metadata
        name: "my-cool-mcp-server",
        version: "1.0.0",
      },
      {
        // Declare capabilities (tools, resources, prompts, logging)
        capabilities: {
          tools: {},
          resources: {},
          // prompts: {},
          // logging: {},
        },
      }
    );

    // ... Define Tools, Resources, Prompts here ...

    // Function to start the server (see "Running the Server" section)
    async function start() {
      console.error("Starting server via stdio...");
      const transport = new StdioServerTransport();
      await server.connect(transport);
      console.error("Server connected.");
    }

    // Only start if not running in a test environment
    if (process.env.NODE_ENV !== 'test') {
       start();
    }
    ```

*   **Python (`server.py`):**
    The Python SDK provides `FastMCP`, a high-level, decorator-based class (inspired by frameworks like FastAPI) for easily defining server capabilities. It's the recommended starting point.
    ```python
    from mcp_sdk import FastMCP # Use FastMCP for the high-level interface
    # StdioServerTransport might be needed depending on how you run it
    # from mcp_sdk.server.stdio import StdioServerTransport
    import asyncio
    import sys
    import logging # Added for clarity

    log = logging.getLogger(__name__) # Basic logger setup
    mcp = FastMCP(
        "my-cool-mcp-server", # Server name
        # version="1.0.0", # Optional version
        # No explicit capabilities dict needed with FastMCP decorators
    )

    # ... Define Tools, Resources, Prompts using @mcp decorators here ...

    # Example runner (adapt as needed, see "Running the Server")
    async def start():
        print("Starting server via stdio...", file=sys.stderr)
        # Transport setup might differ based on how client connects
        # transport = StdioServerTransport()
        # await mcp.run_async(transport=transport) # run_async is common with FastMCP
        print("Server connected/running (or use mcp.run()).", file=sys.stderr)
        # For simple cases, mcp.run() might block and handle transport
        # await asyncio.Event().wait() # May not be needed if mcp.run() blocks

    if __name__ == "__main__":
        # Ensure event loop runs on Windows
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            # Decide how to run: asyncio.run(start()) or mcp.run() directly
            # asyncio.run(start())
            mcp.run() # Often simpler for stdio
        except KeyboardInterrupt:
            print("Server stopped.", file=sys.stderr)
    ```

### 3. Schemas for Inputs (Zod / Pydantic)

MCP relies on JSON Schema to define the expected structure of inputs for Tools and Prompts. The SDKs integrate well with popular validation libraries:

*   **[Zod](https://zod.dev/) (TypeScript):** Used to define input objects and automatically generate JSON Schema.
*   **[Pydantic](https://docs.pydantic.dev/) (Python):** Used to define input models and automatically generate JSON Schema.

You'll see these used extensively in the examples to ensure data passed to your handlers is correctly structured and typed.

## Defining Tools

Tools represent actions or functions the server can perform when requested by the client.

{{ ... }}

**Error Handling in Tools:**

If a tool encounters an error during execution (e.g., failed network request, invalid calculation), it should **throw an Error** (or a custom subclass of Error).

**Why Throw?** The MCP SDK's server framework includes built-in error handling. When you throw an error from your handler, the SDK catches it and automatically formats it into the standard JSON-RPC error response structure required by the MCP protocol before sending it back to the client. This is simpler and more consistent than manually constructing error objects.

```typescript
// examples/typescript-minimal/src/server.ts (Illustrative snippet)
server.tool(
{{ ... }}

## Defining Resources

Resources expose data to the client. They are identified by URIs.

**Resource URI Schemes:** You can define your own URI schemes (e.g., `database://`, `my-api://`, `system://`). Choose schemes that are descriptive and make sense for your server's context. The client will use these exact URIs to request resources.

### Static Resources

{{ ... }}

**TypeScript Handler Signature Note:**

Currently, the TypeScript SDK's type definitions (`ReadResourceTemplateCallback`) do not seem to automatically infer the types of parameters defined in the `ResourceTemplate` (e.g., `{name}`) into the second argument (`variables`). This means a signature like `async (uri, { name }) => { ... }` will likely cause a TypeScript error.

The recommended workaround is to type the second argument as `any` and manually extract/validate the parameters within the handler function. **Be cautious when accessing properties on `handlerArgs: any`**, as they lack compile-time checks. Consider adding runtime checks or type guards if necessary for robustness.

```typescript
// examples/typescript-minimal/src/server.ts
{{ ... }}

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

{{ ... }}
