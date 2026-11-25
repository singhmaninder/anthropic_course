"""
Lesson: Response streaming

The problem streaming solves:
    A normal request waits until Claude has written the entire reply. For long
    answers that can take many seconds, and the user sees nothing meanwhile.
    Streaming sends the reply in small pieces as they are generated, so text
    appears gradually.

How it works:
    It's still ONE request. Claude sends back a series of events:
    - message_start:        a new message begins
    - content_block_start:  a block (text, tool use, ...) begins
    - content_block_delta:  a small piece of the block; for text blocks,
                            this is the new text
    - content_block_stop:   the block is finished
    - message_delta:        final message-level info (stop reason, usage)
    - message_stop:         the message is finished
    (You may also see occasional "ping" events.)

Three ways to stream, shown below:
    1. client.messages.create(..., stream=True): you get every raw event
       and handle them yourself.
    2. client.messages.stream(...) with stream.text_stream: the SDK gives you
       only the text pieces. This is what you usually want for display.
    3. stream.get_final_message(): after streaming, get the fully assembled
       message, e.g. to save in a database.

Key takeaways:
    - Streaming improves perceived speed, not total generation time.
    - Forward each text piece to the client as it arrives; keep the final
      message for storage or further processing.
    - Token usage is still reported, available on the final message.

Changes from the course code:
    - Model updated to a current Haiku (the course's model may be retired).
    - max_tokens lowered to keep token cost down.
    - Raw events are printed by type, so the output is shorter.
"""

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-5-5"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


messages = []
add_user_message(messages, "Write a 1 sentence description of a fake database")

# 1. Raw events: handle every event type yourself
print("--- Raw events ---")
stream = client.messages.create(
    model=model,
    max_tokens=200,
    messages=messages,
    stream=True,
)
for event in stream:
    print(event.type)

# 2. Text only: the SDK filters out everything except the text pieces
print("\n--- Text only ---")
with client.messages.stream(
    model=model,
    max_tokens=200,
    messages=messages,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()

# 3. Stream to the user AND keep the complete message afterwards
print("\n--- Stream, then get the final message ---")
with client.messages.stream(
    model=model,
    max_tokens=200,
    messages=messages,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # in a real app: send to the client

    final_message = stream.get_final_message()

print("\n\nFinal text:", final_message.content[0].text)
print("Usage:", final_message.usage)
print("Stop reason:", final_message.stop_reason)
