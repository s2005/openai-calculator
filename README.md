# OpenAI Calculator

A simple calculator that uses OpenAI's function calling to process mathematical expressions and return results in JSON format.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/s2005/openai-calculator.git
   cd openai-calculator
   ```

2. Set up a virtual environment:

   ### On Linux/macOS:
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate   # For bash/zsh
   # OR
   . venv/bin/activate       # Alternative method
   ```

   ### On Windows:
   ```powershell
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   .\venv\Scripts\activate    # For PowerShell
   # OR
   venv\Scripts\activate.bat  # For Command Prompt
   ```

3. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.template` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.template .env
   # Edit .env and add your OpenAI API key
   ```

   Note: On Windows, you can copy the file using:
   ```powershell
   copy .env.template .env
   ```

## Usage

Basic usage:
```bash
python calculator.py "2 + 2"
```

With optional parameters:
```bash
python calculator.py --model gpt-4 --temperature 0.2 "23 * 45"
```

### Command Line Arguments

- `expression`: The mathematical expression to evaluate (required)
- `--model`: OpenAI model to use (default: gpt-3.5-turbo)
- `--temperature`: Temperature for response generation (default: 0.0)

### Example Output

```json
{
  "expression": "2 + 2",
  "result": 4,
  "operation_type": "addition"
}
```

## MCP Calculator Server (Anthropic Protocol)

This server implements Anthropic's Model Context Protocol (MCP) to expose the calculator functionality. It uses the `mcp` Python SDK (version 1.9.0 or higher).

### Installation of MCP tools

The necessary MCP libraries, including the CLI, are part of the project's requirements. If you installed dependencies using `pip install -r requirements.txt`, the MCP tools should be available. The specific dependency is `mcp[cli]>=1.9.0`.

### Running the Server

Ensure your `OPENAI_API_KEY` is correctly set in your `.env` file.

You can run the server using:
```bash
python mcp_calculator_server.py
```
Alternatively, you can use the MCP CLI for development:
```bash
mcp dev mcp_calculator_server.py
```
The server will register with the name "OpenAICalculatorService".

### Exposed Tool

The server exposes the following tool:

-   **Name:** `evaluate_expression`
-   **Description:** Evaluates a mathematical expression using OpenAI's function calling.
-   **Parameters:**
    -   `expression` (string, required): The mathematical expression string to evaluate.
    -   `model` (string, optional, default: 'gpt-3.5-turbo'): The OpenAI model to use (e.g., 'gpt-3.5-turbo', 'gpt-4').
    -   `temperature` (float, optional, default: 0.0): The sampling temperature for generation (0.0 to 2.0).
-   **Returns:** A dictionary containing the evaluation result. This dictionary will include fields like `expression`, `result`, `operation_type`, and `status`. If an error occurs (either in input validation, during the OpenAI call, or if the OpenAI client is not initialized), the dictionary will contain an `error` field and the `status` will be "failed".

### Interaction Example

This server is designed to be used with MCP-compatible clients (e.g., an LLM that supports MCP for tool use). For development and inspection, you can explore using the `mcp` CLI. For instance, after starting the server, you might use commands like `mcp list` or `mcp call` (refer to MCP SDK documentation for precise usage).

A typical interaction flow would be:
1. An MCP client connects to the "OpenAICalculatorService".
2. The client invokes the `evaluate_expression` tool with necessary parameters (e.g., `{"expression": "100 / (5 + 5)"}`).
3. The server executes the tool using the `process_calculation` logic and returns the JSON result to the client.

Example of a successful result structure:
```json
{
  "expression": "100 / (5 + 5)",
  "result": 10,
  "operation_type": "mixed",
  "status": "success"
}
```

### Further Information on MCP

For more details on the Model Context Protocol (MCP) and the design philosophy behind this server's implementation, please refer to `docs/llm.txt`.

## Error Handling

If an error occurs, the output will be in the following format:
```json
{
  "error": "error message",
  "expression": "original expression",
  "status": "failed"
}
```

## Requirements

- Python 3.6+
- OpenAI API key
- Required packages (see requirements.txt):
  - openai>=1.0.0
  - python-dotenv>=0.19.0
  - argparse>=1.4.0
  - mcp[cli]>=1.9.0
  - pydantic>=2.0.0