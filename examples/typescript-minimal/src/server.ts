import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { ResourceContents, TextContent, Prompt, PromptArgument } from "@modelcontextprotocol/sdk/types.js";

// --- Logger Helper ---
// Helper to ensure logs go to stderr for stdio transport
const logInfo = (...args: any[]) => console.error(`[INFO] ${new Date().toISOString()}`, ...args);
const logWarn = (...args: any[]) => console.error(`[WARN] ${new Date().toISOString()}`, ...args);
const logError = (...args: any[]) => console.error(`[ERROR] ${new Date().toISOString()}`, ...args);
const logDebug = (...args: any[]) => console.error(`[DEBUG] ${new Date().toISOString()}`, ...args); // Using console.error for visibility

// --- Server Setup --- //

// 1. Create server instance
// 'enhanced-typescript-server' is the name clients will use.
logInfo('Initializing MCP server...');
const serverOptions = {
  name: "enhanced-typescript-server",
  version: "1.0.0",
  capabilities: {
    // Declare provided capabilities
    tools: {},
    resources: {},
    prompts: {},
    logging: { minLevel: 'INFO' } // Allow client to set min log level
  },
  // Optional: Provide metadata for prompts and resources upfront
  // This helps clients discover them without needing to explicitly list them
  prompts: [
    {
      name: "summarize-text",
      description: "A prompt template to summarize text.",
      arguments: [
        { name: "text_to_summarize", description: "The text content to be summarized.", type: "string", required: true }
      ]
    }
  ],
  resources: [
    {
      uri: "mcp-resource://enhanced-typescript-server/hello",
      name: "Hello Resource",
      description: "A simple static text resource.",
      content_type: "text/plain"
    },
    {
      // URI Template for dynamic resource
      uri: "mcp-resource://enhanced-typescript-server/greeting/{name}",
      name: "Personalized Greeting Resource",
      description: "A dynamic text resource providing a personalized greeting.",
      content_type: "text/plain"
      // Note: Schema for path parameters handled by template matching in handler
    }
  ]
};
const server = new McpServer(serverOptions);

// --- Tools --- //

// 2a. Define the simple echo tool
server.tool(
  "echo", // Tool name
  "Simply returns the message provided.", // Tool description
  {
    // Input schema using Zod
    message: z.string().describe("The string message to echo back."),
  },
  // Handler function for the tool
  async (params: { message: string }) => {
    const inputMessage = params.message;
    logInfo(`Tool 'echo' called with message: "${inputMessage}"`);
    // Return the result structured according to MCP schema
    const result = {
      content: [
        {
          type: "text",
          text: `You sent: ${inputMessage}`,
        } satisfies TextContent,
      ],
    };
    logInfo(`Tool 'echo' completed. Result: ${JSON.stringify(result)}`);
    return result;
  }
);

// 2b. Define the calculate tool
// Define input schema for calculate
const calculateSchema = z.object({
  operand1: z.number().describe("The first number."),
  operand2: z.number().describe("The second number."),
  operation: z.enum(['+', '-', '*', '/']).default('+').describe("The operation: '+', '-', '*', '/'. Defaults to '+'")
});

// Define output structure (though MCP primarily uses content array)
interface CalculationResult {
  operation: string;
  operand1: number;
  operand2: number;
  result: number;
}

server.tool(
  "calculate",
  "Performs a simple calculation (+, -, *, /).",
  calculateSchema.shape,
  async (params): Promise<{ content: TextContent[] }> => {
    const { operand1, operand2, operation } = params;
    logInfo(`Tool 'calculate' called: ${operand1} ${operation} ${operand2}`);

    let result: number;
    try {
      if (operation === '+') {
        logDebug(`Performing addition: ${operand1} + ${operand2}`);
        result = operand1 + operand2;
      } else if (operation === '-') {
        logDebug(`Performing subtraction: ${operand1} - ${operand2}`);
        result = operand1 - operand2;
      } else if (operation === '*') {
        logDebug(`Performing multiplication: ${operand1} * ${operand2}`);
        result = operand1 * operand2;
      } else if (operation === '/') {
        logDebug(`Performing division: ${operand1} / ${operand2}`);
        if (operand2 === 0) {
          logWarn('Attempted division by zero.');
          throw new Error("Division by zero is not allowed.");
        }
        result = operand1 / operand2;
      } else {
        // Should be caught by Zod enum, but belt-and-suspenders
        logWarn(`Invalid operation: ${operation}`);
        throw new Error(`Unsupported operation: ${operation}`);
      }

      // Format result as structured text (MCP standard)
      const output: CalculationResult = {
        operand1,
        operand2,
        operation,
        result
      };

      logInfo(`Tool 'calculate' completed. Result: ${JSON.stringify(output)}`);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(output, null, 2)
          } satisfies TextContent
        ]
      };
    } catch (error) {
        // Log error to server console
        logError(`Calculation failed: ${error instanceof Error ? error.message : String(error)}`);
        // Re-throw to have MCP send an error response to the client
        throw error;
    }
  }
);

// --- Tool: Fetch JSON ---
const fetchJsonParamsSchema = z.object({
  url: z.string().url({ message: "Invalid URL provided." }),
});

server.tool(
  "fetch-json",
  "Fetches JSON data from a provided URL.",
  fetchJsonParamsSchema.shape,
  async ({ url }) => {
    logInfo(`Tool 'fetch-json' called with URL: ${url}`);
    try {
      const response = await fetch(url, {
        signal: AbortSignal.timeout(10000) // 10-second timeout
      });

      if (!response.ok) {
        logWarn(`HTTP error fetching URL ${url}: Status ${response.status}`);
        return {
          content: [], // Add empty content array for error case
          error: { message: `HTTP error: ${response.status} ${response.statusText}` },
        };
      }

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
         logWarn(`Invalid content type received from URL: ${url}, expected JSON.`);
         return {
            content: [], // Add empty content array for error case
            error: { message: "Response content type is not JSON." }
         };
      }

      const jsonData = await response.json();
      logInfo(`Tool 'fetch-json' completed successfully for URL: ${url}. Response size: ${JSON.stringify(jsonData, null, 2).length} chars.`);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(jsonData, null, 2), // Pretty print JSON
        }],
      };
    } catch (error: any) {
      logError(`fetch-json failed for URL ${url}: ${error.message}`); // Server log
      // Throw an error, which the SDK should catch and format into a JSON-RPC error response.
      // This pattern (throwing from handlers) was observed in community examples
      // (e.g., Falkicon/mcp-server-template) and seems preferred over returning an error object.
      throw new Error(`Failed to fetch or parse JSON from ${url}: ${error.message}`);
    }
  }
);

// --- Resources --- //

// 3. Define the hello resource handler
const HELLO_RESOURCE_URI = "mcp-resource://enhanced-typescript-server/hello";

server.resource(
  "hello-resource",
  HELLO_RESOURCE_URI,
  async (uri: URL): Promise<any> => { 
    logInfo(`Resource requested: ${uri.href}`);
    const resourceContent = { 
        uri: uri.toString(), 
        content_type: "text/plain",
        content: [
            { type: "text", text: "Hello from the enhanced TypeScript MCP server!" } satisfies TextContent
        ]
    }; 
    logInfo(`Resource '${HELLO_RESOURCE_URI}' completed. Content type: text/plain`);
    return resourceContent; 
  }
);

// --- Dynamic Greeting Resource --- //
const GREETING_RESOURCE_URI_TEMPLATE = "mcp-resource://enhanced-typescript-server/greeting/{name}";

// Define the handler using 'handlerArgs: any' as a workaround.
// The SDK's type definitions for the ReadResourceTemplateCallback do not seem
// to correctly infer or type the parameters defined in the ResourceTemplate
// (like '{name}' here) into the second argument ('variables: Variables').
// Attempting to use the signature 'async (uri, { name }: { name: string }) => { ... }'
// results in a TypeScript error (No overload matches...).
// Using 'any' bypasses this type check, but requires manual extraction and type checking.
// TODO: Revisit if SDK types are updated or clearer examples become available.
const greetingHandler = async (uri: URL, handlerArgs: any): Promise<any> => { 
  logInfo(`Dynamic resource requested: ${uri.href}`);

  // Manually extract 'name' from the handlerArgs object and provide a default.
  // The exact structure of handlerArgs might vary, requiring inspection or safer access.
  const name = handlerArgs?.name ?? "DefaultName";
  logInfo(`Name parameter from handlerArgs: ${name}`);

  const textString = `Hello, ${name}! This is a dynamic greeting from the TypeScript server.`;
  const resourceContent = { 
    uri: uri.toString(),
    content_type: "text/plain",
    content: [
        { type: "text", text: textString } satisfies TextContent
    ]
  };
  logInfo(`Resource '${uri.href}' completed. Content: '${textString.substring(0, 50)}...' (truncated)`);
  return resourceContent; 
};

// Register the dynamic resource using the template
server.resource(
  "greeting-resource",
  new ResourceTemplate(GREETING_RESOURCE_URI_TEMPLATE, { list: undefined }),
  greetingHandler // Use the handler defined above
);

// --- Prompts --- //

// 4. Define the summarize prompt handler
const SUMMARY_PROMPT_NAME = "summarize-text";

server.prompt(
  SUMMARY_PROMPT_NAME,
  // Define input schema for the prompt arguments
  z.object({
    text_to_summarize: z.string().describe("The text content to be summarized.")
  }).shape,
  async (args: { text_to_summarize: string }) => {
    logInfo(`Prompt requested: ${SUMMARY_PROMPT_NAME} with text length: ${args.text_to_summarize.length}`);
    // Define message structure inline, using TextContent for content field and literal type for role
    const userMessage: { role: "user" | "assistant"; content: TextContent } = {
      role: "user",
      // Content must be a structured object
      content: {
        type: "text",
        text: `Please summarize the following text:\n\n${args.text_to_summarize}`
      }
    };
    // Return only the messages array structure as expected by server.prompt
    return {
      messages: [userMessage]
    };
  }
);

// --- Run Server --- //

// 5. Run the server using stdio transport
async function main() {
  logInfo(`Starting MCP server '${serverOptions.name}' version ${serverOptions.version}...`);
  const transport = new StdioServerTransport();
  try {
    await server.connect(transport);
    logInfo("Server connected via stdio. Waiting for requests...");
    // Keep the server running (transport handling keeps it alive)
  } catch (error) {
    logError("Failed to connect server transport:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  logError("Fatal error during server execution:", error);
  process.exit(1);
});

// Basic handling for graceful shutdown
process.on('SIGINT', () => {
  logInfo('Received SIGINT. Shutting down...');
  // Perform any cleanup here if needed
  process.exit(0);
});
process.on('SIGTERM', () => {
  logInfo('Received SIGTERM. Shutting down...');
  // Perform any cleanup here if needed
  process.exit(0);
});
