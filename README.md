# Anthropic Course

A collection of small, practical Python examples for learning how to work with the Anthropic API. Each lesson is intentionally focused on one concept and can be run independently.

## Requirements

- Python 3.12 or newer
- An Anthropic API key
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Setup

Clone the repository and install its dependencies:

```powershell
git clone <repository-url>
cd anthropic_course
uv sync
```

Create a `.env` file in the project root:

```dotenv
ANTHROPIC_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and should not be committed.

## Run the course examples

Run a lesson directly with `uv`:

```powershell
uv run python 01_basics/making_a_request.py
```

The project package can also be run with:

```powershell
uv run anthropic-course
```

## Course structure

- `01_basics/` - Introductory examples, including creating a client and sending a first message.
- `src/anthropic_course/` - Python package entry point.

## Dependencies

- `anthropic` - Anthropic Python SDK
- `python-dotenv` - Loads environment variables from `.env`