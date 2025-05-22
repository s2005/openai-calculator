import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# Attempt to import from calculator.py
try:
    from calculator import process_calculation, load_environment as load_calculator_env
except ImportError as e:
    # This will allow the server to start but log an error if calculator components are missing.
    # Actual calculation calls will fail later if this happens.
    process_calculation = None
    load_calculator_env = None
    print(f"Warning: Could not import from calculator.py: {e}. Calculation endpoint will not work fully.")

# Configure basic logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Use Flask's logger after basicConfig has been set.
# If specific handlers or formatting for app.logger beyond basicConfig are needed,
# they can be added here (e.g., app.logger.addHandler(...)).
# For now, basicConfig should cover console output.

# Global OpenAI client
client = None

def initialize_openai_client():
    """
    Loads environment variables and initializes the OpenAI client.
    Returns the client instance or raises EnvironmentError if API key is missing.
    """
    global client
    try:
        if load_calculator_env: # Check if function was imported
            load_calculator_env() # This will raise EnvironmentError if key is missing
        else:
            # Fallback or direct check if load_calculator_env is not available
            if not os.getenv('OPENAI_API_KEY'):
                raise EnvironmentError("OPENAI_API_KEY not found in environment variables and load_calculator_env is unavailable.")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key: # Double check, though load_calculator_env should catch this
             raise EnvironmentError("OPENAI_API_KEY not found after attempting to load environment.")
        client = OpenAI(api_key=api_key)
        print("OpenAI client initialized successfully.")
    except EnvironmentError as e:
        print(f"Error initializing OpenAI client: {e}")
        # Depending on desired behavior, you might want to exit or let Flask start with a non-functional client
        # For now, we'll let it start but client will be None, and endpoints using it will fail.
        client = None 
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI client initialization: {e}")
        client = None


@app.route('/calculate', methods=['POST'])
def handle_calculate():
    """
    Handles calculation requests.
    """
    # Log incoming request (get_json() is called again, but it's usually fine for logging)
    # Alternatively, log `data` after it's first obtained and validated.
    # Using request.data might log raw bytes; get_json() is better for structured logging if JSON is expected.
    app.logger.info(f"Received /calculate request from {request.remote_addr} with JSON data: {request.get_json(silent=True)}") # silent=True to avoid raising error here if not JSON

    if not request.is_json:
        response_data = {"error": "Invalid request: Content-Type must be application/json"}
        app.logger.error(f"Sending error response (400): {response_data}")
        return jsonify(response_data), 400

    data = request.get_json() # This is the primary call for data handling
    if not data: 
        response_data = {"error": "Invalid request: Malformed JSON or empty payload"}
        app.logger.error(f"Sending error response (400): {response_data}")
        return jsonify(response_data), 400

    expression = data.get('expression')
    if not expression:
        response_data = {"error": "Invalid request: 'expression' is required"}
        app.logger.error(f"Sending error response (400): {response_data}")
        return jsonify(response_data), 400

    # Check if OpenAI client is initialized
    if client is None:
        response_data = {"error": "OpenAI client not initialized. Check API key or server logs."}
        app.logger.error(f"Sending error response (503): {response_data}")
        return jsonify(response_data), 503

    # Check if process_calculation was imported
    if process_calculation is None:
        response_data = {"error": "Calculation logic is unavailable due to import error. Check server logs."}
        app.logger.error(f"Sending error response (503): {response_data}")
        return jsonify(response_data), 503

    model = data.get('model', 'gpt-3.5-turbo')
    temperature = data.get('temperature', 0.0)

    try:
        # Call the imported process_calculation function
        result = process_calculation(
            client=client,
            expression=expression,
            model=model,
            temperature=temperature
        )
        
        app.logger.info(f"Sending successful response (200): {result}")
        return jsonify(result)

    except Exception as e:
        # Log the exception details using app.logger
        app.logger.error(f"Unexpected error during calculation: {e}", exc_info=True) # exc_info=True logs stack trace
        response_data = {"error": "Calculation failed due to an internal server error"}
        app.logger.error(f"Sending error response (500): {response_data}")
        return jsonify(response_data), 500

if __name__ == '__main__':
    # Initialize client on startup
    initialize_openai_client()
    
    # Note: In a production environment, use a WSGI server like Gunicorn or uWSGI
    # instead of Flask's built-in development server.
    app.run(debug=True, host='0.0.0.0', port=5000)
