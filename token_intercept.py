# vllm_intercept.py

import openai
import os

# Set the API base to your local server
openai.api_base = os.environ.get("OPENAI_API_BASE", "http://localhost:8000/v1")

# Set the API key to a dummy value (since you're using a local server)
openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-dummy")

# Save the original ChatCompletion.create method
original_chat_completion_create = openai.ChatCompletion.create

def chat_completion_create_intercept(*args, **kwargs):
    """
    Intercepts calls to openai.ChatCompletion.create and redirects them to the local vLLM server.
    """
    # Map the model name to the local model
    model = kwargs.get("model", "")
    if model == "gpt-3.5-turbo":
        kwargs["model"] = "facebook/opt-125m"
    else:
        kwargs["model"] = model  # Use the specified model

    # Convert 'messages' to a single 'prompt'
    messages = kwargs.get("messages", [])
    prompt = ""
    for message in messages:
        role = message.get('role', '')
        content = message.get('content', '')
        if role == 'system':
            prompt += f"{content}\n"
        elif role == 'user':
            prompt += f"User: {content}\n"
        elif role == 'assistant':
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"

    # Remove 'messages' and add 'prompt'
    kwargs.pop('messages', None)
    kwargs['prompt'] = prompt

    # Call the Completion endpoint instead
    response = openai.Completion.create(*args, **kwargs)

    # Modify the response to match the ChatCompletion format
    for choice in response.get('choices', []):
        text = choice.pop('text', '')
        choice['message'] = {
            'role': 'assistant',
            'content': text.strip()
        }
        # Remove keys that are not part of the ChatCompletion response
        choice.pop('logprobs', None)
        choice.pop('finish_reason', None)

    return response

# Override the ChatCompletion.create method
openai.ChatCompletion.create = chat_completion_create_intercept