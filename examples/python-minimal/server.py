import logging
from mcp.server.fastmcp import FastMCP
from mcp.model.resource import ResourceMetadata, ResourceContent
from mcp.model.prompt import PromptArgument, PromptMetadata, Prompt
from mcp.model.message import Message
from typing import TypedDict, List
import asyncio
import aiohttp
import json
from pydantic import BaseModel, Field, HttpUrl

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# 1. Initialize FastMCP server
# 'enhanced-python-server' is the name clients will use to identify this server.
mcp = FastMCP(
    "enhanced-python-server",
    capabilities=["tools", "resources", "prompts", "logging"]
)

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
    log.info(f"Calculate tool called: {a} {operation} {b}")
    result: float
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        if b == 0:
            log.error("Division by zero attempted")
            raise ValueError("Division by zero is not allowed.")
        result = a / b
    else:
        log.warning(f"Unsupported operation: {operation}")
        raise ValueError(f"Unsupported operation: {operation}. Use 'add', 'subtract', 'multiply', or 'divide'.")

    # Return the result as a string, matching the TypeScript example
    return str(result)

# --- Tool: Fetch JSON ---
class FetchJsonParams(BaseModel):
    url: HttpUrl = Field(..., description="The URL to fetch JSON data from.")

@mcp.tool(
    name="fetch-json",
    description="Fetches JSON data from a given URL.",
    input_schema=FetchJsonParams,
)
async def fetch_json(params: FetchJsonParams) -> dict:
    """
    Asynchronously fetches JSON content from a URL.
    """
    url_str = str(params.url) # Convert pydantic HttpUrl back to string for aiohttp
    log.info(f"Tool 'fetch-json' called with URL: {url_str}")
    timeout = aiohttp.ClientTimeout(total=10) # Set a 10-second timeout
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url_str) as response:
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                try:
                    # Check content type before decoding
                    if 'application/json' not in response.headers.get('Content-Type', ''):
                         log.error(f"Invalid content type received from URL: {url_str}, expected JSON.")
                         return {"error": {"message": "Response content type is not JSON."}}
                    json_data = await response.json(content_type=None) # Use content_type=None to bypass strict check, already checked manually
                    return {"content": [{"type": "text", "text": json.dumps(json_data, indent=2)}]}
                except json.JSONDecodeError:
                    log.error(f"Failed to decode JSON from URL: {url_str}")
                    return {"error": {"message": "Failed to decode JSON from response."}}
                # ContentTypeError might not be needed if checking manually
                # except aiohttp.ContentTypeError:
                #      logger.error(f"Invalid content type received from URL: {url_str}, expected JSON.")
                #      return {"error": {"message": "Response content type is not JSON."}}

    except aiohttp.ClientResponseError as e:
        log.error(f"HTTP error fetching URL {url_str}: Status {e.status}, Message: {e.message}")
        return {"error": {"message": f"HTTP error: {e.status} {e.message}"}}
    except aiohttp.ClientConnectionError as e:
        log.error(f"Connection error fetching URL {url_str}: {e}")
        return {"error": {"message": f"Connection error: {e}"}}
    except aiohttp.ClientError as e:
        log.error(f"General HTTP client error fetching URL {url_str}: {e}")
        return {"error": {"message": f"HTTP client error: {e}"}}
    except asyncio.TimeoutError:
         log.error(f"Request timed out fetching URL {url_str}")
         return {"error": {"message": "Request timed out."}}
    except Exception as e:
        log.exception(f"Unexpected error fetching URL {url_str}: {e}")
        return {"error": {"message": f"An unexpected error occurred: {e}"}}

# --- Resources --- #

# Define a simple resource
HELLO_RESOURCE_URI = "mcp-resource://enhanced-python-server/hello"

@mcp.resource(HELLO_RESOURCE_URI)
def get_hello_resource() -> ResourceContent:
    """Provides a simple 'Hello' resource."""
    log.info(f"Resource requested: {HELLO_RESOURCE_URI}")
    return ResourceContent(
        uri=HELLO_RESOURCE_URI,
        content_type="text/plain",
        content="Hello from the Enhanced Python MCP Server!" # Updated message
    )

# Resource Metadata (optional but recommended for client discovery)
mcp.add_resource_metadata(
    ResourceMetadata(
        uri=HELLO_RESOURCE_URI,
        name="Hello Resource",
        description="A simple static text resource.",
        content_type="text/plain"
    )
)

# --- Dynamic Resource --- #

# Define a resource URI template with a parameter
GREETING_RESOURCE_URI_TEMPLATE = "mcp-resource://enhanced-python-server/greeting/{name}"

@mcp.resource(GREETING_RESOURCE_URI_TEMPLATE)
def get_greeting_resource(name: str) -> ResourceContent:
    """Provides a personalized greeting resource based on the name in the URI."""
    log.info(f"Dynamic resource requested: {GREETING_RESOURCE_URI_TEMPLATE} with name='{name}'")
    uri = GREETING_RESOURCE_URI_TEMPLATE.format(name=name)
    return ResourceContent(
        uri=uri,
        content_type="text/plain",
        content=f"Hello, {name}! This is a dynamic greeting from the Python server."
    )

# Dynamic Resource Metadata (optional but recommended for client discovery)
mcp.add_resource_metadata(
    ResourceMetadata(
        uri=GREETING_RESOURCE_URI_TEMPLATE,
        name="Personalized Greeting Resource",
        description="A dynamic text resource providing a personalized greeting.",
        content_type="text/plain",
        # Indicate path parameters if your SDK supports it explicitly in metadata
        # (mcp.py uses the URI template string directly for matching)
    )
)

# --- Prompts --- #

# Define a simple prompt template
SUMMARY_PROMPT_NAME = "summarize-text"

@mcp.prompt(SUMMARY_PROMPT_NAME)
def get_summary_prompt(text_to_summarize: str) -> Prompt:
    """Generates a prompt to ask an LLM to summarize the provided text."""
    log.info(f"Prompt requested: {SUMMARY_PROMPT_NAME}")
    user_message = Message(role="user", content=f"Please summarize the following text:\n\n{text_to_summarize}")
    return Prompt(messages=[user_message])

# Prompt Metadata (optional but recommended for client discovery)
mcp.add_prompt_metadata(
    PromptMetadata(
        name=SUMMARY_PROMPT_NAME,
        description="A prompt template to summarize text.",
        arguments=[
            PromptArgument(name="text_to_summarize", description="The text content to be summarized.", type="string", required=True)
        ]
    )
)

# --- Run Server --- #

# Run the server using stdio transport
if __name__ == "__main__":
    log.info("Starting enhanced Python MCP server on stdio...")
    mcp.run(transport='stdio')
