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

## MCP Server Usage

The Multi-Calculator Proxy (MCP) server provides an HTTP API for calculations.

### Running the Server

To start the server, run:
```bash
python mcp_server.py
```
By default, the server listens on `http://0.0.0.0:5000/`.

### API Endpoint

- **Method:** `POST`
- **URL:** `/calculate`

### Request Format

- **Content-Type:** `application/json`
- **Body:** A JSON object with the following fields:
    - `expression` (string, required): The mathematical expression to evaluate.
    - `model` (string, optional): The OpenAI model to use (e.g., "gpt-3.5-turbo"). Defaults to the server's pre-configured default if not provided.
    - `temperature` (float, optional): The temperature for the OpenAI API response generation. Defaults to the server's pre-configured default if not provided.

### Example Request (using `curl`)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"expression": "5 * (3+2)"}' http://localhost:5000/calculate
```

### Example Response

A successful calculation will return a JSON response similar to this:
```json
{
  "expression": "5 * (3+2)",
  "result": 25,
  "operation_type": "mixed",
  "status": "success" 
}
```
Note: The `status` field indicates "success". Error responses will also be in JSON format and typically include an "error" field and "status": "failed", similar to the command-line tool.

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
  - Flask>=2.0.0