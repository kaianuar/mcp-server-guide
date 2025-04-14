import logging
from mcp.server import FastMCP
from mcp.types import ResourceContents, Resource, TextContent, TextResourceContents
from mcp.types import PromptArgument, Prompt
from mcp.types import SamplingMessage
from typing import TypedDict, List, Dict, Any, Optional
import asyncio
import aiohttp
import json
from pydantic import BaseModel, Field, HttpUrl
import sys
import random
import aiofiles
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stderr)
log = logging.getLogger(__name__)

# 1. Initialize FastMCP server
# 'enhanced-python-server' is the name clients will use to identify this server.
mcp = FastMCP(
    "enhanced-python-server",
    capabilities=["tools", "resources", "prompts", "logging"]
)

log.info(f"MCP Server '{mcp.name}' initialized.")

# --- Tools --- #

# Define a tool with numeric inputs and string output
@mcp.tool()
def calculate(a: float, b: float, operation: str = 'add') -> str:
    """Performs a simple calculation (add, subtract, multiply, divide).

    Args:
        a: The first number.
        b: The second number.
        operation: The operation to perform ('add', 'subtract', 'multiply', 'divide'). Defaults to 'add'.
    """
    log.info(f"Tool 'calculate' called with a={a}, b={b}, operation='{operation}'")
    result: float
    if operation == 'add':
        log.debug(f"Performing addition: {a} + {b}")
        result = a + b
    elif operation == 'subtract':
        log.debug(f"Performing subtraction: {a} - {b}")
        result = a - b
    elif operation == 'multiply':
        log.debug(f"Performing multiplication: {a} * {b}")
        result = a * b
    elif operation == 'divide':
        log.debug(f"Performing division: {a} / {b}")
        if b == 0:
            log.warning("Attempted division by zero.")
            raise ValueError("Cannot divide by zero")
        result = a / b
    else:
        log.warning(f"Invalid operation '{operation}' requested.")
        raise ValueError(f"Invalid operation: {operation}")

    response_str = str(result)
    log.info(f"Tool 'calculate' completed. Result: {response_str}")
    return response_str

# --- Tool: Fetch JSON ---
class FetchJsonParams(BaseModel):
    url: HttpUrl = Field(..., description="The URL to fetch JSON data from.")

@mcp.tool(
    name="fetch-json",
    description="Fetches JSON data from a given URL.",
)
async def fetch_json(params: FetchJsonParams) -> str:
    """
    Asynchronously fetches JSON content from a URL.

    Raises:
        ValueError: If the response content type is not JSON or JSON decoding fails.
        aiohttp.ClientResponseError: For HTTP status errors (4xx, 5xx).
        aiohttp.ClientConnectionError: For connection-related errors.
        asyncio.TimeoutError: If the request times out.
        aiohttp.ClientError: For other client-side HTTP errors.
        Exception: For unexpected errors during the process.
    """
    url_str = str(params.url) # Convert pydantic HttpUrl back to string for aiohttp
    log.info(f"Tool 'fetch-json' called with URL: {url_str}")
    timeout = aiohttp.ClientTimeout(total=10) # Set a 10-second timeout
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url_str) as response:
                # Raise ClientResponseError for bad status codes (4xx or 5xx)
                # This is caught by the except block below
                response.raise_for_status()

                # Check content type before decoding
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                     log.error(f"Invalid content type received from URL: {url_str}, Content-Type: '{content_type}'. Expected JSON.")
                     raise ValueError(f"Response content type is not JSON (got '{content_type}')")

                try:
                    # Use content_type=None to bypass strict check, already checked manually
                    json_data = await response.json(content_type=None)
                    # Return the JSON data as a pretty-printed string directly
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError as e:
                    log.error(f"Failed to decode JSON from URL: {url_str}: {e}")
                    raise ValueError(f"Failed to decode JSON from response: {e}")

    except aiohttp.ClientResponseError as e:
        log.error(f"HTTP error fetching URL {url_str}: Status {e.status}, Message: {e.message}")
        # Re-raise the specific HTTP error
        raise
    except aiohttp.ClientConnectionError as e:
        log.error(f"Connection error fetching URL {url_str}: {e}")
        # Re-raise the specific connection error
        raise
    except aiohttp.ClientError as e: # Catch other general client errors
        log.error(f"General HTTP client error fetching URL {url_str}: {e}")
        # Re-raise the specific client error
        raise
    except asyncio.TimeoutError:
         log.error(f"Request timed out fetching URL {url_str}")
         # Re-raise the timeout error
         raise
    except ValueError as e: # Catch specific ValueErrors raised above
        log.error(f"Data validation error for URL {url_str}: {e}")
        # Re-raise the ValueError (e.g., bad content type, JSON decode error)
        raise
    except Exception as e: # Catch any other unexpected errors
        log.exception(f"Unexpected error fetching URL {url_str}: {e}") # Use log.exception
        # Re-raise the unexpected error
        raise

# --- Sampling Example Tool --- #

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
    """Generates a creative text response, varying based on temperature."""
    log.info(f"Tool 'creative_response' called with prompt: '{params.prompt}', temperature: {params.temperature}")
 
    # Predefined responses
    responses = [
        f"A very straightforward answer about: {params.prompt}",
        f"Thinking outside the box regarding: {params.prompt}",
        f"A whimsical take on: {params.prompt}",
        f"Let's get abstract with: {params.prompt}"
    ]
 
    # Simple logic based on temperature
    if params.temperature < 0.3:
        # Low temperature -> more deterministic
        chosen_response = responses[0]
        log.debug("Low temperature, choosing deterministic response.")
    elif params.temperature > 0.8:
        # High temperature -> more random (choose from all)
        chosen_response = random.choice(responses)
        log.debug("High temperature, choosing random response from all options.")
    else:
        # Medium temperature -> slightly less deterministic (choose from first two)
        chosen_response = random.choice(responses[:2])
        log.debug("Medium temperature, choosing random response from first two options.")
 
    log.info(f"Tool 'creative_response' completed. Response: '{chosen_response}'")
    return chosen_response

# --- File I/O Tools --- #

# Define a safe base directory for file operations
SANDBOX_DIR = Path(__file__).parent / "sandbox"
SANDBOX_DIR.mkdir(exist_ok=True) # Create sandbox if it doesn't exist

def _resolve_sandbox_path(filename: str) -> Path:
    """Resolves a filename to an absolute path within the sandbox, preventing escape."""
    # Normalize the filename to prevent directory traversal
    # os.path.normpath might be another option, but Path resolves '..' safely.
    # Security: Ensure the resolved path is still inside the sandbox
    resolved_path = SANDBOX_DIR.joinpath(filename).resolve()
    if SANDBOX_DIR not in resolved_path.parents and resolved_path != SANDBOX_DIR:
         # This check prevents resolving paths like ../../etc/passwd
         raise ValueError(f"Path '{filename}' attempts to escape the sandbox directory.")
    return resolved_path

class ReadFileParams(BaseModel):
    filename: str = Field(..., description="The name of the file to read within the sandbox.")

@mcp.tool(
    name="read_file",
    description="Reads the content of a specified file within the server's sandbox directory.",
)
async def read_file_tool(params: ReadFileParams) -> str:
    try:
        target_path = _resolve_sandbox_path(params.filename)
        log.info(f"Attempting to read file: {target_path}")
        if not target_path.is_file():
            log.warning(f"File not found or is not a file: {target_path}")
            return f"Error: File not found or is not a regular file: {params.filename}"

        async with aiofiles.open(target_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
        log.info(f"Successfully read file: {target_path}")
        return content
    except ValueError as e:
        log.error(f"Path validation error for '{params.filename}': {e}")
        return f"Error: Invalid filename. {e}"
    except Exception as e:
        log.exception(f"Error reading file '{params.filename}': {e}")
        return f"Error: Could not read file '{params.filename}'. {e}"

class WriteFileParams(BaseModel):
    filename: str = Field(..., description="The name of the file to write within the sandbox.")
    content: str = Field(..., description="The text content to write to the file.")

@mcp.tool(
    name="write_file",
    description="Writes text content to a specified file within the server's sandbox directory.",
)
async def write_file_tool(params: WriteFileParams) -> str:
    try:
        target_path = _resolve_sandbox_path(params.filename)
        log.info(f"Attempting to write to file: {target_path}")

        # Security: Ensure we don't overwrite directories
        if target_path.is_dir():
             log.warning(f"Attempted to write to a directory: {target_path}")
             return f"Error: Cannot write to '{params.filename}' as it is a directory."

        async with aiofiles.open(target_path, mode='w', encoding='utf-8') as f:
            await f.write(params.content)

        log.info(f"Successfully wrote to file: {target_path}")
        return f"Successfully wrote content to '{params.filename}'."
    except ValueError as e:
        log.error(f"Path validation error for '{params.filename}': {e}")
        return f"Error: Invalid filename. {e}"
    except Exception as e:
        log.exception(f"Error writing file '{params.filename}': {e}")
        return f"Error: Could not write to file '{params.filename}'. {e}"

# --- Resources --- #

# Define a simple resource
HELLO_RESOURCE_URI = "mcp-resource://enhanced-python-server/hello"

@mcp.resource(HELLO_RESOURCE_URI)
def get_hello_resource() -> ResourceContents:
    """Provides a simple 'Hello' resource."""
    log.info(f"Resource '{HELLO_RESOURCE_URI}' requested.")
    content = ResourceContents(
        uri=HELLO_RESOURCE_URI,
        content_type="text/plain",
        content="Hello from the Enhanced Python MCP Server!" # Updated message
    )
    log.info(f"Resource '{HELLO_RESOURCE_URI}' completed. Content type: {content.content_type}")
    return content

# Resource registration (the @mcp.resource decorator above already registers the resource)
# No need for separate metadata registration in this version of the SDK
# The FastMCP class handles resource registration through the decorator

# --- Dynamic Resource --- #

# Define a resource URI template with a parameter
GREETING_RESOURCE_URI_TEMPLATE = "mcp-resource://enhanced-python-server/greeting/{name}"

@mcp.resource(GREETING_RESOURCE_URI_TEMPLATE)
def get_greeting_resource(name: str) -> ResourceContents:
    """Provides a personalized greeting resource based on the name in the URI."""
    log.info(f"Resource '{GREETING_RESOURCE_URI_TEMPLATE}' requested for name='{name}'")
    uri = GREETING_RESOURCE_URI_TEMPLATE.format(name=name)
    text_content = f"Hello, {name}! This is a dynamic greeting from the Python server."
    content = ResourceContents(
        uri=uri,
        content_type="text/plain",
        content=text_content
    )
    log.info(f"Resource '{uri}' completed. Content: '{text_content[:50]}...' (truncated)")
    return content

# Dynamic Resource registration (the @mcp.resource decorator above already registers the resource)
# No need for separate metadata registration in this version of the SDK
# The FastMCP class handles resource registration through the decorator

# --- Prompts --- #

# Define a simple prompt template
SUMMARY_PROMPT_NAME = "summarize-text"

@mcp.prompt(SUMMARY_PROMPT_NAME)
def get_summary_prompt(text_to_summarize: str) -> Prompt:
    """Generates a prompt to ask an LLM to summarize the provided text."""
    log.info(f"Prompt requested: {SUMMARY_PROMPT_NAME}")
    user_message = Message(role="user", content=f"Please summarize the following text:\n\n{text_to_summarize}")
    return Prompt(messages=[user_message])

# Prompt registration (the @mcp.prompt decorator above already registers the prompt)
# No need for separate metadata registration in this version of the SDK
# The FastMCP class handles prompt registration through the decorator

# --- Run Server --- #

# Run the server using stdio transport
if __name__ == "__main__":
    log.info("Preparing to run MCP server...")
    # Ensure event loop runs on Windows
    if sys.platform == "win32":
        log.debug("Applying WindowsSelectorEventLoopPolicy for asyncio.")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        log.info(f"Starting MCP server '{mcp.name}' via mcp.run()...")
        mcp.run() # This handles stdio transport and blocks until client disconnects or error
        log.info(f"MCP server '{mcp.name}' finished running.")
    except KeyboardInterrupt:
        log.info("Server stopped by user (KeyboardInterrupt).")
    except Exception as e:
        log.exception("MCP server encountered an unexpected error during run.")
    finally:
        log.info("Server process exiting.")
