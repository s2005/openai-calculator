import pytest
import json
from unittest import mock

# Import the Flask app instance from your mcp_server module
from mcp_server import app as flask_app
import mcp_server # To allow patching mcp_server.client and mcp_server.process_calculation

@pytest.fixture
def client():
    """
    Pytest fixture to create a Flask test client.
    Ensures the app is in testing mode.
    """
    flask_app.config['TESTING'] = True
    # The global mcp_server.client and mcp_server.process_calculation
    # will be patched within individual tests as needed.
    with flask_app.test_client() as test_client:
        yield test_client

def test_calculate_success(client):
    """Test successful calculation."""
    expected_result = {"expression": "2+2", "result": 4, "operation_type": "addition", "status": "success"}
    
    with mock.patch('mcp_server.process_calculation', return_value=expected_result) as mock_process, \
         mock.patch('mcp_server.client', new_callable=mock.Mock) as mock_oai_client: # Ensure client is not None
        
        # Ensure the mock_oai_client is not None for this test path
        mcp_server.client = mock_oai_client 

        response = client.post('/calculate', json={"expression": "2+2"})
        
        assert response.status_code == 200
        assert response.json == expected_result
        mock_process.assert_called_once_with(
            client=mock_oai_client,
            expression="2+2",
            model='gpt-3.5-turbo', # Default model
            temperature=0.0       # Default temperature
        )

def test_calculate_missing_expression(client):
    """Test request with missing 'expression' field."""
    with mock.patch('mcp_server.client', new_callable=mock.Mock): # Ensure client is not None
        response = client.post('/calculate', json={})
        assert response.status_code == 400
        assert "error" in response.json
        assert response.json["error"] == "Invalid request: 'expression' is required"

def test_calculate_invalid_content_type(client):
    """Test request with invalid Content-Type."""
    with mock.patch('mcp_server.client', new_callable=mock.Mock): # Ensure client is not None
        response = client.post('/calculate', data="not json", content_type="text/plain")
        assert response.status_code == 400
        assert "error" in response.json
        assert response.json["error"] == "Invalid request: Content-Type must be application/json"

def test_calculate_malformed_json(client):
    """Test request with malformed JSON."""
    with mock.patch('mcp_server.client', new_callable=mock.Mock): # Ensure client is not None
        response = client.post('/calculate', data="{malformed_json", content_type="application/json")
        assert response.status_code == 400 # Flask's default for unparseable JSON
        assert "error" in response.json
        assert "Malformed JSON" in response.json["error"] # Or similar, depends on Flask version

def test_calculate_process_calculation_returns_error(client):
    """Test when process_calculation itself returns an error dictionary."""
    error_result = {"error": "Division by zero", "expression": "1/0", "status": "failed"}
    
    with mock.patch('mcp_server.process_calculation', return_value=error_result) as mock_process, \
         mock.patch('mcp_server.client', new_callable=mock.Mock) as mock_oai_client:
        mcp_server.client = mock_oai_client
        
        response = client.post('/calculate', json={"expression": "1/0"})
        
        assert response.status_code == 200 # As per current design
        assert response.json == error_result
        mock_process.assert_called_once()

def test_calculate_with_model_and_temperature(client):
    """Test that model and temperature are passed to process_calculation."""
    expected_result = {"expression": "3*3", "result": 9, "operation_type": "multiplication", "status": "success"}
    
    with mock.patch('mcp_server.process_calculation', return_value=expected_result) as mock_process, \
         mock.patch('mcp_server.client', new_callable=mock.Mock) as mock_oai_client:
        mcp_server.client = mock_oai_client

        response = client.post('/calculate', json={
            "expression": "3*3",
            "model": "gpt-4",
            "temperature": 0.5
        })
        
        assert response.status_code == 200
        assert response.json == expected_result
        mock_process.assert_called_once_with(
            client=mock_oai_client,
            expression="3*3",
            model='gpt-4',
            temperature=0.5
        )

def test_calculate_openai_client_not_initialized(client):
    """Test 503 error when mcp_server.client is None."""
    # Temporarily set the global client in mcp_server to None for this test
    original_client = mcp_server.client
    mcp_server.client = None
    
    try:
        response = client.post('/calculate', json={"expression": "1+1"})
        assert response.status_code == 503
        assert "error" in response.json
        assert "OpenAI client not initialized" in response.json["error"]
    finally:
        # Restore the original client to avoid affecting other tests
        mcp_server.client = original_client

def test_calculate_process_calculation_not_imported(client):
    """Test 503 error when mcp_server.process_calculation is None (simulating import error)."""
    original_process_calculation = mcp_server.process_calculation
    mcp_server.process_calculation = None # Simulate import failure
    
    # Need to ensure mcp_server.client is not None for this test to isolate the process_calculation check
    with mock.patch('mcp_server.client', new_callable=mock.Mock) as mock_oai_client:
        # If the original client was already mocked or None, this ensures it's a valid mock for this specific test path
        original_global_client = mcp_server.client 
        mcp_server.client = mock_oai_client

        try:
            response = client.post('/calculate', json={"expression": "1+1"})
            assert response.status_code == 503
            assert "error" in response.json
            assert "Calculation logic is unavailable" in response.json["error"]
        finally:
            # Restore original process_calculation and client
            mcp_server.process_calculation = original_process_calculation
            mcp_server.client = original_global_client

# A simple test to ensure pytest is running
def test_pytest_setup():
    assert True
