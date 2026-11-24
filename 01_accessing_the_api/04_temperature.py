"""
Lesson: Temperature

What the original course teaches:
    Temperature (0.0 to 1.0) controls how random the model's output is.
    Low values give more predictable answers, high values give more varied ones.

What changed since the course was recorded:
    - Python SDK v1.0 removed `temperature`, `top_p` and `top_k` from
      messages.create(), so passing them raises a TypeError.
    - API version 2026-10-21 (the default in SDK 2.0) rejects these
      parameters on every model with a 400 error, even at the default value.
    - Newer models already rejected non-default values before that.
    - Even at temperature 0.0, output was never guaranteed to be identical.

What I do instead:
    Steer variety through the prompt. This is a nudge, not an exact control.
    For repeatable results (e.g. evals), don't depend on identical outputs.
    Use a grader that tolerates variation.

Migration guide: https://platform.claude.com/docs/en/api/migration-2026-10-21
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
        "max_tokens": 1000,
        "messages": messages,
        # NOTE: no "temperature" here. It was removed from the API.
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text


# Predictable-style output (replaces temperature=0.0)
messages = []
add_user_message(
    messages,
    "Generate a one sentence movie idea. Give the most typical, conventional idea.",
)
print("Predictable-style answer:", chat(messages))

# Creative-style output (replaces temperature=1.0)
messages = []
add_user_message(
    messages,
    "Generate a one sentence movie idea. Make it wildly original and unexpected.",
)
print("\nCreative-style answer:", chat(messages))
