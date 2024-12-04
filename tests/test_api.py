import os
from openai import OpenAI

def test_api_connection():
    client = OpenAI()  # This will use OPENAI_API_KEY from environment
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print("API Connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection()