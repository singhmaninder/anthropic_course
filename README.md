# Anthropic Course

A collection of small, practical Python lessons for learning how to use the Anthropic API. Lessons are organized by topic and progress from basic API requests to advanced agent workflows.

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

## Course lessons

### 01. Accessing the API

Run the lessons in order:

```powershell
uv run python 01_accessing_the_api/01_making_a_request.py
uv run python 01_accessing_the_api/02_multi_turn_conversation.py
uv run python 01_accessing_the_api/03_system_prompt.py
```

| Lesson | Concepts covered |
| --- | --- |
| `01_making_a_request.py` | Create an Anthropic client, configure a model, send a message, and print the response |
| `02_multi_turn_conversation.py` | Build a message history and send a follow-up request with conversation context |
| `03_system_prompt.py` | Add a system prompt and compare responses with and without it |

### 02. Prompt Evaluation

Examples for evaluating prompts and comparing model behavior.

### 03. Prompt Engineering

Examples for improving prompts through structured instructions and techniques.

### 04. Tool Use

Examples for giving Claude access to tools and handling tool interactions.

### 05. RAG and Agentic Search

Examples for retrieval-augmented generation and agent-driven information search.

### 06. Claude Features

Examples for Claude-specific capabilities, including extended thinking.

### 07. MCP

Examples for connecting Claude to external tools and data through Model Context Protocol.

### 08. Agents and Workflows

Examples for building multi-step agent and workflow patterns.

The lesson folders under `02_` through `08_` are available for upcoming examples and currently contain limited or placeholder implementations.

## Project package

The package entry point is available as:

```powershell
uv run anthropic-course
```

## Course structure

- `01_accessing_the_api/` - Basic API access, multi-turn conversations, and system prompts.
- `02_prompt_evaluation/` - Prompt evaluation examples.
- `03_prompt_engineering/` - Prompt engineering examples.
- `04_tool_use/` - Tool-use examples.
- `05_rag_and_agentic_search/` - RAG and agentic search examples.
- `06_claude_features/` - Claude-specific feature examples.
- `07_mcp/` - Model Context Protocol examples.
- `08_agents_and_workflows/` - Agent and workflow examples.
- `src/anthropic_course/` - Package entry point for the project command.
- `.env` - Local API key configuration; this file is not tracked by Git.

## Dependencies

- `anthropic` - Anthropic Python SDK
- `python-dotenv` - Loads environment variables from `.env`