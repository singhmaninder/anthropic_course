"""
Lesson: Multi-turn conversations

What the lesson teaches:
    The API is stateless: Claude doesn't remember earlier requests. To have a
    conversation, you keep a list of messages yourself and send the WHOLE
    list every time.

How it works:
    1. Add the user's message to the list.
    2. Send the list to Claude and get a reply.
    3. Add Claude's reply to the list as an "assistant" message.
    4. Add the next user message, then repeat.

What this script shows:
    - First question: "Define quantum computing in one sentence".
    - Follow-up: "Write another sentence". This only makes sense because the
      full history, including Claude's first answer, is sent along with it.

Key takeaways:
    - Messages alternate between roles: "user" and "assistant".
    - You must append Claude's reply to the history yourself, otherwise the
      next request has no memory of it.
    - Longer history means more input tokens, so cost grows with each turn.

Changes from the course code:
    - Model updated to a current Haiku (the course's model may be retired).
    - max_tokens lowered from 1000 to 300 to keep token cost down.
"""

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-5-5"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=300,
        messages=messages,
    )
    return message.content[0].text


# Start with an empty message list
messages = []
print("Starting a conversation with Claude...")

# Add the initial user question
add_user_message(messages, "Define quantum computing in one sentence")

# Get Claude's response and save it to the history
answer = chat(messages)
add_assistant_message(messages, answer)
print("Claude's response:", answer)
print("Conversation history:", messages)

# Add a follow-up question
add_user_message(messages, "Write another sentence")
print("\nConversation history after follow-up question:", messages)

# Get the follow-up response, with the full context sent again
final_answer = chat(messages)
add_assistant_message(messages, final_answer)
print("\nFinal answer:", final_answer)
print("Final conversation history:", messages)
