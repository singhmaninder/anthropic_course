from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-4-5"

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text

# Start with an empty message list
messages = []
print("Starting a conversation with Claude...")

# Add the initial user question
add_user_message(messages, "Define quantum computing in one sentence")

# Get Claude's response
answer = chat(messages)
add_assistant_message(messages, answer)
print("Claude's response:", answer)
print("Conversation history:", messages)

# Add a follow-up question
add_user_message(messages, "Write another sentence")
print("\nConversation history after follow-up question:", messages)

# Get the follow-up response with full context
final_answer = chat(messages)
add_assistant_message(messages, final_answer)
print("\nFinal answer:", final_answer)
print("Final conversation history:", messages)