#!/usr/bin/env python3
"""
OpenAI Calculator - A simple calculator that uses OpenAI's function calling
to process mathematical expressions and return results in JSON format.
"""

import argparse
import json
import os
import sys
import re
from typing import Dict, Any, Union

from dotenv import load_dotenv
from openai import OpenAI

def validate_expression(expression: str) -> Union[bool, str]:
    """Validate the mathematical expression."""
    # Check for multiple operators
    if re.search(r'[\+\-\*\/]{2,}', expression):
        return "Invalid operator sequence"
    
    # Check for division by zero
    if re.search(r'/\s*0(?![.])', expression):
        return "Division by zero"
    
    # Basic syntax check
    try:
        # Replace all numbers and basic operators with 'x' to check structure
        simplified = re.sub(r'[\d.]+', 'x', expression)
        simplified = re.sub(r'[\+\-\*\/\(\)]', 'x', simplified)
        # If anything other than 'x' and whitespace remains, it's invalid
        if re.search(r'[^\sx]', simplified):
            return "Invalid characters in expression"
    except Exception:
        return "Invalid expression format"
        
    return True

def setup_argparse() -> argparse.ArgumentParser:
    """Configure and return the argument parser."""
    parser = argparse.ArgumentParser(
        description='Calculator using OpenAI function calling with JSON output'
    )
    parser.add_argument(
        'expression',
        type=str,
        help='Mathematical expression to evaluate'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-3.5-turbo',
        help='OpenAI model to use (default: gpt-3.5-turbo)'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.0,
        help='Temperature for response generation (default: 0.0)'
    )
    return parser

def load_environment() -> None:
    """Load environment variables from .env file."""
    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)

def get_calculator_functions() -> list:
    """Define the calculator function schema for OpenAI."""
    return [{
        "name": "calculate",
        "description": "Calculate the result of a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression provided by the user"
                },
                "result": {
                    "type": "number",
                    "description": "The calculated result of the expression"
                },
                "operation_type": {
                    "type": "string",
                    "description": "The type of mathematical operation performed",
                    "enum": ["addition", "subtraction", "multiplication", "division", "mixed"]
                }
            },
            "required": ["expression", "result", "operation_type"]
        }
    }]

def process_calculation(client: OpenAI, args: argparse.Namespace) -> Dict[str, Any]:
    """Process the calculation using OpenAI's function calling."""
    # Validate expression first
    validation_result = validate_expression(args.expression)
    if validation_result is not True:
        return {
            "error": validation_result,
            "expression": args.expression,
            "status": "failed"
        }

    try:
        system_message = """You are a precise calculator. When evaluating mathematical expressions:
1. Always follow standard mathematical order of operations (PEMDAS)
2. For mixed operations, use the 'mixed' operation type
3. Return exact numerical results
4. Validate all inputs thoroughly"""

        response = client.chat.completions.create(
            model=args.model,
            temperature=args.temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": f"Calculate this expression and provide the result: {args.expression}"
                }
            ],
            functions=get_calculator_functions(),
            function_call={"name": "calculate"}
        )

        # Extract the function call from the response
        function_call = response.choices[0].message.function_call
        
        # Parse the calculation result
        return json.loads(function_call.arguments)

    except Exception as e:
        return {
            "error": str(e),
            "expression": args.expression,
            "status": "failed"
        }

def main():
    """Main function to run the calculator."""
    # Load environment variables
    load_environment()

    # Setup argument parser
    parser = setup_argparse()
    args = parser.parse_args()

    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Process the calculation
    result = process_calculation(client, args)

    # Output the result as formatted JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()