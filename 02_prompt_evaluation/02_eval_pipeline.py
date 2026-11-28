"""
Lesson: Eval pipeline with a model grader and a code grader

The idea:
    Every test case is run through the prompt, then graded twice:
      - Model grader: Claude reviews the solution and returns strengths,
        weaknesses, reasoning and a 1-10 score.
      - Code grader:  checks the output actually parses as the expected
        format (python / json / regex). 10 if it parses, 0 if it does not.
    The final score is the average of the two.

Dataset format:
    Each test case needs a "format" field so the code grader knows which
    validator to use:
        {"task": "Create a Python function to validate an AWS IAM username",
         "format": "python"}

Notes:
    - No prefill and no stop_sequences. The reply is cleaned in code instead
      (strip_code_fences / extract_json), which works whatever the model does.
    - Results are shown with `rich` and saved to results.json next to this
      script.
    - dataset.json is read from next to this script.
"""

import ast
import json
import re
from pathlib import Path
from statistics import mean

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

client = Anthropic()
model = "claude-haiku-5-5"
console = Console()

# Weights for combining the two graders. Must add up to 1.
MODEL_WEIGHT = 0.5
SYNTAX_WEIGHT = 0.5


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def chat(messages, system=None, max_tokens=1000):
    params = {
        "model": model,
        "max_tokens": max_tokens,
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


# ---------------------------------------------------------------------------
# Output cleaning
# ---------------------------------------------------------------------------
FENCE_RE = re.compile(r"```[a-zA-Z0-9_+-]*\n?(.*?)```", re.DOTALL)


def strip_code_fences(text):
    """If the reply is wrapped in a ``` block, return only what is inside."""
    match = FENCE_RE.search(text)
    return match.group(1).strip() if match else text.strip()


def extract_json(text):
    """Parse a JSON object from a reply, with or without code fences."""
    cleaned = strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back to the outermost {...} in the text
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


# ---------------------------------------------------------------------------
# Prompt under test
# ---------------------------------------------------------------------------
def run_prompt(test_case):
    """Merges the prompt and test case input, then returns the result"""
    prompt = f"""
Please solve the following task:

{test_case["task"]}

* Respond only with {test_case["format"]}
* Do not add any comments, commentary or explanation
* Do not wrap the answer in markdown code fences
"""

    messages = []
    add_user_message(messages, prompt)
    return strip_code_fences(chat(messages))


# ---------------------------------------------------------------------------
# Model grader
# ---------------------------------------------------------------------------
def grade_by_model(test_case, output):
    eval_prompt = f"""
You are an expert code reviewer. Evaluate this AI-generated solution.

Task: {test_case["task"]}
Solution: {output}

Respond with only a JSON object (no other text) with these keys:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your assessment
- "score": A number between 1-10
"""

    messages = []
    add_user_message(messages, eval_prompt)

    eval_text = chat(messages)
    try:
        grade = extract_json(eval_text)
        grade["score"] = float(grade["score"])
        return grade
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return {
            "strengths": [],
            "weaknesses": [],
            "reasoning": "Grader returned invalid JSON",
            "score": 0,
        }


# ---------------------------------------------------------------------------
# Code grader
# ---------------------------------------------------------------------------
def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(output, test_case):
    if test_case["format"] == "json":
        return validate_json(output)
    if test_case["format"] == "python":
        return validate_python(output)
    return validate_regex(output)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_test_case(test_case):
    """Calls run_prompt, then grades the result with both graders"""
    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)
    model_score = model_grade["score"]
    syntax_score = grade_syntax(output, test_case)

    score = MODEL_WEIGHT * model_score + SYNTAX_WEIGHT * syntax_score

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "model_score": model_score,
        "syntax_score": syntax_score,
        "strengths": model_grade.get("strengths", []),
        "weaknesses": model_grade.get("weaknesses", []),
        "reasoning": model_grade.get("reasoning", ""),
    }


def run_eval(dataset):
    """Runs every test case in the dataset and collects the results"""
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([r["score"] for r in results])
    console.print(f"[bold]Average score: {average_score:.2f}[/bold]")

    return results


def print_results(results):
    """Show each result in a panel, rendering Claude's output as Markdown."""
    for i, result in enumerate(results, start=1):
        console.rule(
            f"[bold cyan]Test case {i}[/bold cyan]  |  "
            f"score: {result['score']:.1f}  "
            f"(model: {result['model_score']}, syntax: {result['syntax_score']})"
        )
        console.print(
            Panel(
                f"{result['test_case']['task']}\n"
                f"[dim]format: {result['test_case']['format']}[/dim]",
                title="Task",
                border_style="yellow",
            )
        )
        fmt = result["test_case"]["format"]
        lang = fmt if fmt in ("python", "json") else ""
        console.print(
            Panel(
                Markdown(f"```{lang}\n{result['output']}\n```"),
                title="Output",
                border_style="green",
            )
        )
        console.print(
            Panel(result["reasoning"], title="Grader reasoning", border_style="blue")
        )
        console.print()


if __name__ == "__main__":
    base = Path(__file__).parent
    with open(base / "dataset.json", "r") as f:
        dataset = json.load(f)

    results = run_eval(dataset)
    print_results(results)

    with open(base / "results.json", "w") as f:
        json.dump(results, f, indent=2)
