"""
Lesson: Structured Data

What the original course teaches:

 Structured output helps make model responses easier to parse and use
 in applications.

 Typical use cases:

 - Extracting information from documents
 - Classification tasks
 - Generating machine-readable JSON
 - Building reliable application workflows

 Common techniques included:
 - Asking for JSON
 - Assistant prefilling
 - Stop sequences

 These techniques can improve formatting consistency compared to
 completely free-form text.

What changed since the course was recorded:

 - Assistant prefilling can no longer be used with current Claude
   models. Conversations must end with a user message.

 - Historical examples often used assistant prefilling to nudge
   JSON output, but this technique is no longer available.

 - Stop sequences can accidentally truncate nested structures and leave
   incomplete JSON.

 - Modern models are generally good at following JSON instructions, but
   they can still occasionally produce invalid or unexpected output.

 - Even when a response appears to be valid JSON, it may not match the
   schema your application expects.

What I do instead:

 Ask for a clear schema in the prompt.

 Tell the model to return JSON only.

 Parse the response.

 Validate the result against a schema.

 Handle validation failures and retries gracefully.

 Historical techniques such as assistant prefilling and stop sequences
 can still be useful teaching examples, but they should not be treated
 as reliability mechanisms.

 For production systems, rely on validation rather than assuming the
 model always follows the requested format.

Documentation:
https://platform.claude.com/docs
"""

from dotenv import load_dotenv
import json

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
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text


# --------------------------------------------------
# Historical Example 1: Assistant Prefilling
# --------------------------------------------------

print("=== Historical Example: Assistant Prefilling ===")

print(
    """
Historically, some Claude examples used assistant prefilling:

messages = [
    {
        "role": "user",
        "content": "Generate movie data as JSON."
    },
    {
        "role": "assistant",
        "content": "{"
    }
]

The assistant prefix acted as a hint that the response
should continue as JSON.

This was a formatting nudge, not a guarantee of valid output.

Current Claude models require conversations to end with a
user message, so assistant prefilling is no longer supported.
"""
)


# --------------------------------------------------
# Historical Example 2: Stop Sequences
# --------------------------------------------------

print("\n=== Historical Example: Stop Sequences ===")

print(
    r"""
Some older examples combined JSON prompting
with stop sequences.

For example:

params = {
    "model": model,
    "messages": messages,
    "max_tokens": 1000,
    "stop_sequences": ["\n\nHuman:"]
}

This can help prevent extra text after an answer,
but it does not validate or guarantee JSON.

Using a stop sequence such as '}' can be dangerous
because nested JSON objects contain multiple closing
braces and may be cut off early.

Valid nested JSON:

{
  "movie": {
    "title": "Example"
  }
}

A poorly chosen stop sequence could leave:

{
  "movie": {
    "title": "Example"
  }

which is invalid JSON.
"""
)


# --------------------------------------------------
# Modern Example: Structured Output
# --------------------------------------------------

print("\n=== Modern Example: Structured Output ===")

messages = []

add_user_message(
    messages,
    """
Generate a movie idea.

Return ONLY valid JSON matching this schema:

{
  "title": string,
  "genre": string,
  "summary": string,
  "target_audience": string
}

Do not include markdown.

Do not include explanations.

Return JSON only.
"""
)

response = chat(messages)

print("Raw response:")
print(response)


# --------------------------------------------------
# Parse JSON
# --------------------------------------------------

try:
    data = json.loads(response)

    print("\nSuccessfully parsed JSON:")
    print(json.dumps(data, indent=2))

except json.JSONDecodeError as e:
    print("\nJSON parsing failed:")
    print(e)
    data = None


# --------------------------------------------------
# Schema Validation
# --------------------------------------------------

if data is not None:

    try:
        from pydantic import BaseModel


        class Movie(BaseModel):
            title: str
            genre: str
            summary: str
            target_audience: str


        movie = Movie.model_validate(data)

        print("\nSchema validation succeeded:")
        print(movie)

    except Exception as e:
        print("\nSchema validation failed:")
        print(e)


# --------------------------------------------------
# Classification Example
# --------------------------------------------------

print("\n=== Example: Classification ===")

messages = []

add_user_message(
    messages,
    """
Classify the review below.

Review:
"The battery lasts all day and the screen is beautiful."

Return ONLY valid JSON:

{
  "sentiment": "positive" | "neutral" | "negative",
  "confidence": number
}
"""
)

classification = chat(messages)

print(classification)


# --------------------------------------------------
# Production Guidance
# --------------------------------------------------

print(
    """
Production recommendation:

1. Ask for a clear schema.
2. Request JSON only.
3. Parse the response.
4. Validate against a schema.
5. Retry or handle failures gracefully.

Do not assume that prompting alone guarantees
valid structured output.
"""
)
