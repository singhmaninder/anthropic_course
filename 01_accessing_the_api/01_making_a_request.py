"""
Lesson: Making a request

What the lesson teaches:
    The simplest call to the Claude API: create a client, then call
    client.messages.create() with a model, a token limit, and a list of messages.

The three required parameters:
    - model:      which Claude model to use.
    - max_tokens: the cap on how many tokens Claude can generate in its reply
                  (output only, not the input). It's a limit, not a target.
    - messages:   a list of {"role": ..., "content": ...} dictionaries.
                  Here there's a single "user" message.

The response:
    - message.content is a list of blocks; the text is in content[0].text.
    - message.usage shows input_tokens and output_tokens, which is useful for
      tracking cost.
    - message.stop_reason says why Claude stopped ("end_turn" means it
      finished normally, "max_tokens" means it was cut off).

Key takeaways:
    - The client reads ANTHROPIC_API_KEY from the environment, loaded here
      from .env by python-dotenv.
    - Each request is independent. Claude remembers nothing between calls.

Changes from the course code:
    - Model updated to a current Haiku (the course's model may be retired).
    - max_tokens lowered from 1000 to 200 to keep token cost down.
    - Added printing of usage and stop_reason to see what a response contains.
"""

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-5-5"

message = client.messages.create(
    model=model,
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence",
        }
    ],
)

print(message.content[0].text)
print("\nUsage:", message.usage)
print("Stop reason:", message.stop_reason)
