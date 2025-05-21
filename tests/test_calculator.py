import os
import pytest
import json # Added for creating mock JSON responses
# unittest.mock is part of the standard library.
# pytest-mock provides 'mocker' fixture which is a thin wrapper around unittest.mock.
# No explicit import needed for mocker, it's a fixture.

from openai import OpenAI
from dotenv import load_dotenv

# Import specific functions from calculator module
from calculator import process_calculation, validate_expression 

# Load environment variables from .env file (can remain, but tests won't rely on API_KEY)
load_dotenv()

@pytest.fixture
def openai_client_instance():
    """
    Fixture to provide an OpenAI client instance.
    For these unit tests, the actual API calls will be mocked,
    so a real API key is not strictly necessary for the client instance itself.
    """
    # Passing a dummy API key to satisfy OpenAI library's internal checks if any,
    # but it won't be used for actual calls due to mocking.
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY", "test_key_not_used"))

class TestCalculatorProcessCalculation:
    """
    Tests for the process_calculation function in calculator.py.
    These tests mock the OpenAI API calls.
    """

    def test_basic_addition_success(self, openai_client_instance, mocker):
        """Test basic addition operation with mocked OpenAI call."""
        expression = "2 + 2"
        expected_openai_response_dict = {"expression": expression, "result": 4, "operation_type": "addition"}
        
        # Mock the OpenAI API call
        mock_openai_response = mocker.MagicMock()
        # Simulate the structure of the OpenAI response object
        mock_openai_response.choices = [mocker.MagicMock()]
        mock_openai_response.choices[0].message = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call.arguments = json.dumps(expected_openai_response_dict)
        
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create', return_value=mock_openai_response)
        
        result = process_calculation(openai_client_instance, expression, model="gpt-test", temperature=0.1)
        
        assert result == expected_openai_response_dict # process_calculation should return the parsed dict
        mock_create_method.assert_called_once_with(
            model="gpt-test",
            temperature=0.1,
            messages=[
                {"role": "system", "content": mocker.ANY}, # System message content can be checked if static
                {"role": "user", "content": f"Calculate this expression and provide the result: {expression}"}
            ],
            functions=mocker.ANY, # Function schema can be checked if static
            function_call={"name": "calculate"}
        )

    def test_basic_multiplication_success(self, openai_client_instance, mocker):
        """Test basic multiplication with mocked OpenAI call."""
        expression = "6 * 7"
        expected_openai_response_dict = {"expression": expression, "result": 42, "operation_type": "multiplication"}
        
        mock_openai_response = mocker.MagicMock()
        mock_openai_response.choices = [mocker.MagicMock()]
        mock_openai_response.choices[0].message = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call.arguments = json.dumps(expected_openai_response_dict)
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create', return_value=mock_openai_response)
        
        result = process_calculation(openai_client_instance, expression) # Using default model/temp
        
        assert result == expected_openai_response_dict
        mock_create_method.assert_called_once() # Check if called, specific args checked in other tests

    def test_complex_expression_success(self, openai_client_instance, mocker):
        """Test complex expression with mocked OpenAI call."""
        expression = "(10 + 5) * 2 - 3" 
        # Based on prompt, LLM should eval to 27. (15*2)-3 = 30-3 = 27
        expected_openai_response_dict = {"expression": expression, "result": 27, "operation_type": "mixed"}
        
        mock_openai_response = mocker.MagicMock()
        mock_openai_response.choices = [mocker.MagicMock()]
        mock_openai_response.choices[0].message = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call.arguments = json.dumps(expected_openai_response_dict)
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create', return_value=mock_openai_response)
        
        result = process_calculation(openai_client_instance, expression)
        
        assert result == expected_openai_response_dict
        mock_create_method.assert_called_once()

    def test_invalid_expression_validation_error(self, openai_client_instance, mocker):
        """Test handling of invalid expression (caught by validate_expression)."""
        expression = "2 ++ 2"
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create')
        
        result = process_calculation(openai_client_instance, expression)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == expression
        assert result["error"] == "Invalid operator sequence" 
        mock_create_method.assert_not_called()

    def test_division_by_zero_validation_error(self, openai_client_instance, mocker):
        """Test handling of division by zero (caught by validate_expression)."""
        expression = "1 / 0"
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create')
        
        result = process_calculation(openai_client_instance, expression)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == expression
        assert result["error"] == "Division by zero"
        mock_create_method.assert_not_called()

    def test_invalid_characters_validation_error(self, openai_client_instance, mocker):
        """Test handling of invalid characters (caught by validate_expression)."""
        expression = "2 + abc"
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create')
        
        result = process_calculation(openai_client_instance, expression)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == expression
        assert result["error"] == "Invalid characters in expression"
        mock_create_method.assert_not_called()

    def test_openai_api_error(self, openai_client_instance, mocker):
        """Test handling of an error from the OpenAI API call itself."""
        expression = "10 - 5" 
        
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create', side_effect=Exception("OpenAI API Error"))
        
        result = process_calculation(openai_client_instance, expression)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == expression
        assert result["error"] == "OpenAI API Error" 
        mock_create_method.assert_called_once()

    def test_process_calculation_passes_model_and_temperature(self, openai_client_instance, mocker):
        """Test that model and temperature are correctly passed to OpenAI API."""
        expression = "7 ^ 2"
        custom_model = "gpt-custom"
        custom_temp = 0.75
        expected_openai_response_dict = {"expression": expression, "result": 49, "operation_type": "exponentiation"}

        mock_openai_response = mocker.MagicMock()
        mock_openai_response.choices = [mocker.MagicMock()]
        mock_openai_response.choices[0].message = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call = mocker.MagicMock()
        mock_openai_response.choices[0].message.function_call.arguments = json.dumps(expected_openai_response_dict)
        
        mock_create_method = mocker.patch.object(openai_client_instance.chat.completions, 'create', return_value=mock_openai_response)
        
        result = process_calculation(openai_client_instance, expression, model=custom_model, temperature=custom_temp)
        
        assert result == expected_openai_response_dict
        mock_create_method.assert_called_once_with(
            model=custom_model,
            temperature=custom_temp,
            messages=mocker.ANY, # Or be more specific with the expected messages
            functions=mocker.ANY,
            function_call={"name": "calculate"}
        )

class TestValidateExpression:
    """
    Tests for the validate_expression function directly.
    These do not involve OpenAI calls or mocking.
    """
    def test_valid_simple(self):
        assert validate_expression("1 + 1") is True

    def test_valid_complex(self):
        assert validate_expression("(100 / (2 * 5)) - 1 + 3.14") is True

    def test_invalid_operator_sequence(self):
        assert validate_expression("1 ++ 1") == "Invalid operator sequence"
        assert validate_expression("1 -- 1") == "Invalid operator sequence"
        # Current validator specific to simple arithmetic, not necessarily general purpose for all math
        assert validate_expression("1 ** 1") == "Invalid operator sequence" 
        assert validate_expression("1 // 1") == "Invalid operator sequence"

    def test_division_by_zero_integer(self):
        assert validate_expression("1 / 0") == "Division by zero"
    
    def test_division_by_zero_float(self):
        # The regex `/\s*0(?![.])` specifically avoids matching `/ 0.`
        # So, `1 / 0.0` would be treated as division by zero only if the regex matches.
        # Let's test the exact regex behavior:
        # `re.search(r'/\s*0(?![.])', "1 / 0.0")` -> No match because of `(?![.])`
        # This means the current validator might NOT catch "1 / 0.0" as division by zero if it relies solely on this regex.
        # It depends on how `calculator.py` `validate_expression` handles this.
        # The current `validate_expression` in `calculator.py` seems to only use this regex.
        # This is a subtle point. If the LLM is expected to handle "1/0.0" or if the validator should,
        # then the validator might need adjustment. For now, testing current behavior.
        # The problem description for `validate_expression` in `calculator.py` is:
        # `if re.search(r'/\s*0(?![.])', expression): return "Division by zero"`
        # This regex will not match "1 / 0.0". So it will return True.
        assert validate_expression("1 / 0.0") is True # Based on current regex in calculator.py

    def test_division_by_zero_with_space(self):
        assert validate_expression("1 /  0") == "Division by zero"
        
    def test_division_by_zero_not_at_end(self):
         assert validate_expression("1 / 0 + 1") == "Division by zero"

    def test_no_division_by_zero_with_decimal(self):
        assert validate_expression("1 / 0.5") is True 

    def test_invalid_characters(self):
        assert validate_expression("1 + abc") == "Invalid characters in expression"
        assert validate_expression("1 + $") == "Invalid characters in expression"
        assert validate_expression("eval('1+1')") == "Invalid characters in expression"

    def test_empty_expression(self):
        # Current behavior: simplified becomes '', re.search(r'[^\sx]', '') is False. Returns True.
        assert validate_expression("") is True 

    def test_expression_with_only_spaces(self):
        # Current behavior: simplified becomes '   ', re.search(r'[^\sx]', '   ') is False. Returns True.
        assert validate_expression("   ") is True