import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

# Retrieve the API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Base endpoint for OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Define prompt templates for each tool
tool_prompts = {
    "ai-writer": lambda input_text: f"Write a professional article about: {input_text}",
    "code-assistant": lambda input_text: f"Write a clean, working code snippet to do the following: {input_text}",
    "design-helper": lambda input_text: f"Provide a UI/UX design idea or wireframe layout for: {input_text}",
    "legal-advisor": lambda input_text: f"Generate a simple legal contract or advice for this scenario: {input_text} (not a substitute for legal advice)",
    "health-bot": lambda input_text: f"Provide general health information or advice for: {input_text}. This is not medical advice."
}


def run_tool(tool_name, user_input):
    """
    Given a tool name and user input, sends a formatted prompt to OpenRouter API
    and returns the AI-generated output.
    """

    if tool_name not in tool_prompts:
        return "❌ Tool not recognized. Please select a valid tool."

    prompt = tool_prompts[tool_name](user_input)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4",  # You can change this to mistralai/mixtral, anthropic/claude-3-haiku, etc.
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    except requests.exceptions.RequestException as e:
        return f"⚠️ API request failed: {e}"

    except (KeyError, IndexError):
        return "⚠️ Unexpected response format from OpenRouter."


# Optional test
if __name__ == "__main__":
    output = run_tool("ai-writer", "The importance of clean energy")
    print(output)
