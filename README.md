# OpenAI Calculator

A simple calculator that uses OpenAI's function calling to process mathematical expressions and return results in JSON format.

## Setup

1. Clone this repository
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.template .env
   # Edit .env and add your OpenAI API key
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