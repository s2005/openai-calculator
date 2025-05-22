"""
MCP Server for the OpenAI Calculator.

This server exposes the calculator functionality (from calculator.py)
as a tool through the Model Context Protocol.
"""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from openai import OpenAI # Ensure OpenAI is imported

from mcp.server.fastmcp import FastMCP
# Context might be needed if tools return Context objects, but here we return dicts.
# from mcp.server.fastmcp import Context 
# from pydantic import BaseModel # If defining complex Pydantic types for tool args

# Import necessary components from calculator.py
try:
    from calculator import process_calculation, load_environment
except ImportError as e:
    print(f"Error importing from calculator.py: {e}. Ensure calculator.py is in the same directory or PYTHONPATH.")
    process_calculation = None 
    load_environment = None

# Global placeholder for OpenAI client, to be initialized by the lifespan manager
openai_client: OpenAI | None = None

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """
    Manages the application's lifespan for initializing and cleaning up resources.
    Initializes the OpenAI client.
    """
    global openai_client
    print("Initializing Calculator Service...")
    try:
        if load_environment:
            load_environment() # From calculator.py
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Error: OPENAI_API_KEY not found after loading environment.")
                openai_client = None
            else:
                openai_client = OpenAI(api_key=api_key)
            print("OpenAI client initialized." if openai_client else "OpenAI client FAILED to initialize (API key missing or load_environment failed).")
        else:
            print("Error: load_environment function not available from calculator.py. Cannot initialize OpenAI client.")
            openai_client = None
        yield
    except Exception as e:
        print(f"Error during app lifespan initialization: {e}")
        openai_client = None # Ensure client is None on error
        yield # Still need to yield to complete the context manager protocol
    finally:
        print("Calculator Service shutting down...")

# Initialize FastMCP with the lifespan manager
mcp = FastMCP(
    name="OpenAICalculatorService",
    description="An MCP server that uses OpenAI to evaluate mathematical expressions.",
    lifespan=app_lifespan
)

@mcp.tool()
def evaluate_expression(expression: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.0) -> dict:
    """
    Evaluates a mathematical expression using OpenAI's function calling.

    :param expression: The mathematical expression string to evaluate.
    :param model: The OpenAI model to use (e.g., 'gpt-3.5-turbo', 'gpt-4').
    :param temperature: The sampling temperature for generation (0.0 to 2.0).
    :return: A dictionary containing the evaluation result or an error.
    """
    if not process_calculation:
        return {"error": "Calculator logic (process_calculation) not available due to import error.", "status": "failed"}
    if not openai_client:
        return {"error": "OpenAI client not initialized. Check server logs for API key issues or initialization errors.", "status": "failed"}
    
    # The refactored process_calculation from calculator.py should handle its own exceptions
    # and return a dict with an "error" key if something goes wrong.
    return process_calculation(client=openai_client, expression=expression, model=model, temperature=temperature)

if __name__ == "__main__":
    if process_calculation is None or load_environment is None:
        print("Critical error: Core functions from calculator.py could not be imported. Server cannot start reliably.")
        # Depending on desired behavior, you might exit here:
        # import sys
        # sys.exit(1)
    else:
        print("Starting MCP Calculator Server directly via mcp.run()...")
        # This makes the script runnable with `python mcp_calculator_server.py`
        # For production, usually `mcp run` or an ASGI server like uvicorn is used.
        mcp.run()
