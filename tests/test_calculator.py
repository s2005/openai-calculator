import os
import pytest
from openai import OpenAI
from dotenv import load_dotenv
from calculator import process_calculation

# Load environment variables from .env file
load_dotenv()

class MockArgs:
    """Mock class to simulate argparse.Namespace"""
    def __init__(self, expression, model="gpt-4o-mini", temperature=0.0):
        self.expression = expression
        self.model = model
        self.temperature = temperature

@pytest.fixture
def openai_client():
    """Fixture to provide OpenAI client"""
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("OpenAI API key not found")
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not found")
class TestCalculator:
    def test_basic_addition(self, openai_client):
        """Test basic addition operation"""
        args = MockArgs("2 + 2")
        result = process_calculation(openai_client, args)
        
        assert result["result"] == 4
        assert result["operation_type"] == "addition"
        assert "error" not in result

    def test_basic_multiplication(self, openai_client):
        """Test basic multiplication operation"""
        args = MockArgs("6 * 7")
        result = process_calculation(openai_client, args)
        
        assert result["result"] == 42
        assert result["operation_type"] == "multiplication"
        assert "error" not in result

    def test_complex_expression(self, openai_client):
        """Test more complex mathematical expression"""
        args = MockArgs("(10 + 5) * 2 - 3")
        result = process_calculation(openai_client, args)
        
        assert result["result"] == 22  # (10 + 5) * 2 - 3 = 25 * 2 - 3 = 22
        assert result["operation_type"] == "mixed"
        assert "error" not in result

    def test_invalid_expression(self, openai_client):
        """Test handling of invalid mathematical expression"""
        args = MockArgs("2 ++ 2")
        result = process_calculation(openai_client, args)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == "2 ++ 2"
        assert result["error"] == "Invalid operator sequence"

    def test_division_by_zero(self, openai_client):
        """Test handling of division by zero"""
        args = MockArgs("1 / 0")
        result = process_calculation(openai_client, args)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["expression"] == "1 / 0"
        assert result["error"] == "Division by zero"

    def test_invalid_characters(self, openai_client):
        """Test handling of invalid characters in expression"""
        args = MockArgs("2 + abc")
        result = process_calculation(openai_client, args)
        
        assert "error" in result
        assert result["status"] == "failed"
        assert result["error"] == "Invalid characters in expression"