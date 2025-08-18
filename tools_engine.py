import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Map tools to OpenRouter model IDs
TOOL_MODEL_MAP = {
    "ai-writer": "openai/gpt-3.5-turbo",
    "code-assistant": "openai/gpt-4-turbo",
    "design-helper": "meta-llama/llama-3-70b",
    "legal-advisor": "anthropic/claude-3-haiku",
    "health-bot": "mistralai/mixtral-8x7b"
}

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def run_tool(tool_name, user_input):
    model = TOOL_MODEL_MAP.get(tool_name, "openai/gpt-3.5-turbo")
    system_prompt = generate_prompt(tool_name)

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(API_URL, json=data, headers=HEADERS)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]

        log_interaction(tool_name, user_input, ai_reply)
        return ai_reply

    except Exception as e:
        error_msg = f"⚠️ Error using {tool_name} ({model}): {str(e)}"
        log_interaction(tool_name, user_input, error_msg)
        return error_msg

def generate_prompt(tool_name):
    prompts = {
        "ai-writer": "You are an AI writing assistant that creates blog posts, emails, or documents.",
        "code-assistant": "You are an expert programmer. Help with code, bugs, and examples.",
        "design-helper": "You are a UX/UI design assistant. Help generate mockups and wireframe ideas.",
        "legal-advisor": "You are an AI legal assistant. Provide helpful templates and explanations. Not legal advice.",
        "health-bot": "You are a helpful health chatbot. Offer general health information. Do not provide medical advice."
    }
    return prompts.get(tool_name, "You are an AI assistant.")

def log_interaction(tool, prompt, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n[{timestamp}] TOOL: {tool}\nUSER INPUT: {prompt}\nRESPONSE: {response}\n{'-'*50}\n"

    os.makedirs("logs", exist_ok=True)
    with open("logs/tool_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
