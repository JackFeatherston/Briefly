import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env into the environment
load_dotenv()

# Access the API key from environment variables
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Hardcoded test message
messages = [
    {"role": "user", "content": "Tell me a fun fact about space."}
]

# Send request
response = client.chat.completions.create(
    model="meta-llama/llama-3.3-70b-instruct",
    messages=messages,
    temperature=0.7,
    max_tokens=150
)

# Print result
print("Assistant says:", response.choices[0].message.content)
