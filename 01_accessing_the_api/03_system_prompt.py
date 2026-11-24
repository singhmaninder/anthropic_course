"""
Lesson: System prompts

What the lesson teaches:
    A system prompt gives Claude instructions about HOW to respond (its role,
    tone, and rules), separate from WHAT the user is asking. It's passed in a
    top-level `system` parameter, not inside the messages list.

What this script shows:
    The same question ("How do I solve 5x + 3 = 18?") asked twice:
    1. Without a system prompt: Claude just solves it.
    2. With a "patient math tutor" system prompt: Claude guides step by step
       and doesn't give the answer straight away.

Key takeaways:
    - `system` is optional, so it's only added to the request when provided.
    - The system prompt shapes behavior without changing the user's message.
    - Good system prompts state a role plus clear rules ("do not directly
      answer, guide step by step").
    - Outputs vary between runs, so exact wording will differ each time.

Changes from the course code:
    - Model updated to a current Haiku (the course's model may be retired).
    - max_tokens lowered from 1000 to 500 to keep token cost down.
"""

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-5-5"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def chat(messages, system=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    # Only include the system prompt if one was given
    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text


# Start with an empty message list
messages = []

# Add the initial user question
add_user_message(messages, "How do I solve 5x + 3 = 18?")

# Without a system prompt: Claude answers directly
answer = chat(messages)
print("Claude's response without system prompt:", answer)

# With a system prompt: Claude acts as a tutor
system = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""
answer = chat(messages, system=system)
print("\nClaude's response with system prompt:", answer)
