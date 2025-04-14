# Enhanced TypeScript MCP Server Example

This directory contains an enhanced example of a Model Context Protocol (MCP) server written in TypeScript using the `@modelcontextprotocol/sdk`.

This server demonstrates:
- Basic server setup with name and version.
- Declaring server capabilities (tools, resources, prompts).
- Implementing a simple `echo` tool.
- Implementing a `calculate` tool with input validation (Zod) and error handling.
- Implementing a static `hello` resource (`mcp-resource://enhanced-typescript-server/hello`).
- Implementing a dynamic `greeting` resource (`mcp-resource://enhanced-typescript-server/greeting/{name}`).
- Implementing an asynchronous `fetch-json` tool that retrieves JSON data from a URL.
- Implementing a `summarize-text` prompt template.
- Implementing a `creative_response` tool that generates a creative text response based on a prompt.
- Implementing `readFile` and `writeFile` tools for accessing files within a safe `sandbox` directory.
- Server-side logging using `console.error`.
- Running the server using the `StdioServerTransport`.

## Capabilities

- **Tools:**
  - `echo`: Takes a string message and returns it.
  - `calculate`: Takes two numbers and an operation (+, -, \*, /) and returns the result.
  - `fetch-json`: Takes a URL and returns the fetched JSON data, pretty-printed.
    *   **Error Handling:** Note that the `fetch-json` handler uses a `try...catch` block and `throw new Error(...)` to signal errors. The MCP SDK catches these errors and formats the response.
  - `creative_response`: Generates a creative text response based on a prompt, with randomness controlled by a `temperature` parameter.
    *   **Arguments (Zod schema):**
      - `prompt` (string, required): The input text prompt.
      - `temperature` (float, optional, default: 0.7, range: 0.0-1.0): Controls the randomness of the response selection. Lower values (e.g., 0.1) are more deterministic, while higher values (e.g., 0.9) are more random.
    *   **Returns:** `string` (the generated response).
    *   **Example Call (JSON Arguments):**
      ```json
      {
        "prompt": "Explain quantum physics simply",
        "temperature": 0.5
      }
      ```
  - `readFile`: Asynchronously reads content from a file within a safe `sandbox` directory.
  - `writeFile`: Asynchronously writes content to a file within a safe `sandbox` directory.
- **Resources:**
  - `mcp-resource://enhanced-typescript-server/hello`: A static resource returning a greeting message (`text/plain`).
  - `mcp-resource://enhanced-typescript-server/greeting/{name}`: A dynamic resource returning a personalized greeting based on the `{name}` provided in the URI (`text/plain`).
    *   **Handler Signature:** Due to current limitations in the MCP TypeScript SDK's type inference for `ResourceTemplate` callbacks, the handler for this resource in `src/server.ts` uses `handlerArgs: any` for the second argument. The `name` parameter is then manually extracted from `handlerArgs`. See the comments in `src/server.ts` for more details.
    *   **Note on Resource Handler Types:** Due to type mismatches encountered with the `@modelcontextprotocol/sdk@1.8.0` version, the return type for resource handlers (`hello-resource` and the `greetingHandler` template) has been temporarily set to `Promise<any>`. This bypasses strict TypeScript checking to allow the server to run correctly. Ideally, this should be revisited if clearer type definitions or examples become available for this SDK version.
- **Prompts:**
  - `summarize-text`: A template for generating a prompt to summarize text.
    - Arguments:
      - `text_to_summarize` (string): The text to be summarized.
      - `operation` (string, optional, default: 'add', options: 'add', 'subtract', 'multiply', 'divide')
    - Returns: `string` (representing the result)
- **Logging:** Server logs informational messages and errors to `stderr`.

## Setup

1. Ensure you have Node.js and npm installed.
2. Navigate to this directory (`examples/typescript-minimal`).
3. Install dependencies:
   ```bash
   npm install
   ```

## Running the Server

1. Compile the TypeScript code:
   ```bash
   npm run build
   ```
2. Run the compiled JavaScript code:
   ```bash
   node dist/server.js
   ```

The server will start and listen for MCP messages on standard input/output.

## Interacting with the Server

You can use an MCP client (like the MCP Inspector tool or another application integrated with the SDK) to connect to this server via stdio and interact with its capabilities.

## Usage

Once the server is running (using `npm start` or `npm run dev`), you can interact with it using the `mcp-cli`. Ensure you have `mcp-cli` installed (`npm install -g @modelcontextprotocol/cli`).

**Connect to the Server:**

Use the `stdio` transport to connect:

```bash
mcp connect stdio --command "npm run start"
# Or if already running separately:
mcp connect stdio --command "node build/server.js"
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

```bash
mcp-cli resource fetch mcp-resource://enhanced-typescript-server/hello
```

**4. Fetch the dynamic `greeting` resource:**

```bash
mcp-cli resource fetch mcp-resource://enhanced-typescript-server/greeting/Friend
mcp-cli resource fetch mcp-resource://enhanced-typescript-server/greeting/TypeScript
```

**5. Use the `fetch-json` tool:**

```bash
# Fetch a sample post from JSONPlaceholder
mcp-cli tool fetch-json --url https://jsonplaceholder.typicode.com/posts/1
```

**6. Use the `summarize-text` prompt:**

```bash
mcp-cli prompt summarize-text --text_to_summarize "TypeScript is a free and open-source high-level programming language developed by Microsoft that adds static typing with optional type annotations to JavaScript."
```

**7. Use the `creative_response` tool:**

```bash
mcp-cli tool creative_response --prompt "Explain quantum physics simply" --temperature 0.5
```

**8. Use the `writeFile` tool (creates sandbox/hello_ts.txt):**

```bash
mcp-cli tool writeFile --filename "hello_ts.txt" --content "Hello from the writeFile tool (TS)!"
```

**9. Use the `readFile` tool (reads sandbox/hello_ts.txt):**

```bash
mcp-cli tool readFile --filename "hello_ts.txt"
```

**10. Disconnect:**

```
> disconnect
# or Ctrl+C
```

### `readFile`

Reads the text content of a specified file. **Note:** For security, this tool can only access files within the `examples/typescript-minimal/sandbox/` directory.

**Parameters:**

*   `filename` (string, required): The name of the file to read (relative to the sandbox directory).

**Returns:** An MCP content object containing the file content (`{ content: [{ type: 'text', text: '...' }] }`) or throws an error.

**Example Call (JSON Arguments):**

```json
{
  "params": {
    "filename": "data_from_ts.txt"
  }
}
```

### `writeFile`

Writes text content to a specified file. **Note:** For security, this tool can only write files within the `examples/typescript-minimal/sandbox/` directory. It will create the file if it doesn't exist, or overwrite it if it does.

**Parameters:**

*   `filename` (string, required): The name of the file to write (relative to the sandbox directory).
*   `content` (string, required): The text content to write.

**Returns:** An MCP content object containing a success message (`{ content: [{ type: 'text', text: '...' }] }`) or throws an error.

**Example Call (JSON Arguments):**

```json
{
  "params": {
    "filename": "ts_output.log",
    "content": "Log entry from TypeScript: Process completed."
  }
}
```

For detailed information on the Model Context Protocol, refer to the [official specification](https://github.com/modelcontext/specification).
