"""
Lesson: Generating a test dataset for prompt evaluation

The idea:
    To evaluate a prompt you need many test inputs. An evaluation dataset is a
    list of inputs (here, JSON objects with a "task" field). For each prompt
    and input pair, you later run the prompt and grade the output.
    You can write the dataset by hand or have Claude generate it.

The scenario:
    A prompt that helps users write AWS-related code. The output must be one of
    three kinds: Python, a JSON config, or a regular expression, with no extra
    explanation, headers or footers.

What this script does:
    1. Asks Claude to generate task descriptions as a JSON array.
    2. Parses the reply into a Python list.
    3. Saves it to dataset.json for the evaluation step later.

Key takeaways:
    - Use a fast, cheap model (Haiku) for generating test data.
    - Parsing model output as JSON is fragile, so the prompt says "return only
      the JSON array" and a helper strips any ```json fence Claude adds.
    - Saving the dataset to a file lets you reuse the same inputs in every
      eval run, so prompt versions are compared fairly.

Changes from the course code:
    - Model updated to a current Haiku.
    - `temperature` removed: it is no longer part of the API.
    - Assistant prefill (starting Claude's reply with ```json) removed: newer
      models reject a trailing assistant message with a 400 error.
    - Stop sequences no longer needed, since there is no prefill to pair with.
    - Fixed the example JSON in the prompt (the course's example had a
      trailing comma, which is invalid JSON).
    - dataset.json is saved next to this script, whatever folder you run from.
    - A future option: structured outputs, which enforce a JSON shape.
"""

import json
from pathlib import Path

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
    }
    if system:
        params["system"] = system

    response = client.messages.create(**params)
    return response.content[0].text


def extract_json(text):
    """Remove a ```json ... ``` code fence if Claude added one."""
    text = text.strip()
    if text.startswith("```"):
        # Drop the opening fence line (``` or ```json)
        text = text.split("\n", 1)[1] if "\n" in text else ""
        # Drop the closing fence
        text = text.rsplit("```", 1)[0]
    return text.strip()


def generate_dataset(count=3):
    prompt = f"""
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects, each representing a task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {{
    "task": "Description of task",
    "format": "python" | "json" | "regex"
  }}
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code
* Return only the JSON array, with no other text

Please generate {count} objects.
"""
    messages = []
    add_user_message(messages, prompt)
    text = chat(messages)

    try:
        return json.loads(extract_json(text))
    except json.JSONDecodeError:
        print("Could not parse Claude's reply as JSON. Raw reply:\n")
        print(text)
        raise


if __name__ == "__main__":
    dataset = generate_dataset()
    print(json.dumps(dataset, indent=2))

    output_path = Path(__file__).parent / "dataset.json"
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"\nSaved {len(dataset)} tasks to {output_path}")
