"""
Lesson: Building the core evaluation pipeline

The idea:
    An eval pipeline takes every test case in the dataset, merges it with the
    prompt, sends it to Claude, and grades the output. This script builds
    everything except the real grader, which comes in the next lessons.

The three functions:
    - run_prompt(test_case):  merges the prompt template with one test case,
                              calls Claude, and returns the output text.
    - run_test_case(test_case): calls run_prompt, then grades the result.
                              Grading is a placeholder (score = 10) for now.
    - run_eval(dataset):      loops over all test cases and collects results.

Each result has three fields:
    - output:    Claude's full response
    - test_case: the original input
    - score:     the grade (hardcoded to 10 until graders are built)

Key takeaways:
    - The prompt here is deliberately simple, with no formatting instructions,
      so outputs will be verbose. Improving the prompt is the next step, and
      the eval is how you measure whether a change helps.
    - Most of an eval pipeline is this simple loop. The hard parts are better
      prompts and better graders.
    - Each test case is one API call, so cost grows with dataset size.

Changes from the course code:
    - Model updated to a current Haiku.
    - `temperature` and `stop_sequences` removed from chat(), since they are
      not needed here and temperature is no longer part of the API.
    - chat() joins only the text blocks of the reply, because the first
      content block can be a thinking block, which has no `.text`.
    - Results are shown with `rich` (panels and Markdown) instead of raw
      json.dumps, which shows newlines as literal \\n and is hard to read.
    - Raw results are also saved to results.json next to this script.
    - dataset.json is read from next to this script, whatever folder you run
      from. Run generate_test_dataset.py first to create it.
"""

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

client = Anthropic()
model = "claude-haiku-5-5"
console = Console()


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

    # The reply can contain several blocks (e.g. thinking, then text).
    # Join only the text blocks.
    return "".join(
        block.text for block in response.content if block.type == "text"
    )


def run_prompt(test_case):
    """Merges the prompt and test case input, then returns the result"""
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""

    messages = []
    add_user_message(messages, prompt)
    return chat(messages)


def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)

    # TODO: replace with real grading (model-based or code-based)
    score = 10

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
    }


def run_eval(dataset):
    """Runs every test case in the dataset and collects the results"""
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    return results


def print_results(results):
    """Show each result in a panel, rendering Claude's output as Markdown."""
    for i, result in enumerate(results, start=1):
        console.rule(
            f"[bold cyan]Test case {i}[/bold cyan]  |  score: {result['score']}"
        )
        console.print(
            Panel(result["test_case"]["task"], title="Task", border_style="yellow")
        )
        console.print(
            Panel(Markdown(result["output"]), title="Output", border_style="green")
        )
        console.print()


if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "dataset.json"
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    results = run_eval(dataset)
    print_results(results)
