# LLM Resume File Assistant

A Python CLI tool for searching, reading, and summarizing resume files using OpenAI or OpenRouter tool calling.

## Features

- s_tools.py: 
ead_file, list_files, write_file, and search_in_file.
- PDF (text-based), DOCX, and TXT resume extraction with metadata and contextual matches.
- Strict workspace-relative paths and safe new-file writes (.txt/.md).
- OpenAI Responses and OpenRouter Chat Completions with visible tool execution logs.
- Eight fictional sample resumes for local testing.
- Offline tests for both providers and all four file tools.

## Quick start (Python 3.11+)

On Windows PowerShell:

`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
`

On macOS or Linux:

`ash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
`

If you already have a .env, edit it in place. Keep .env out of version control.

### OpenRouter

Create a key and set these values in .env. [OpenRouter API keys](https://openrouter.ai/keys)

`dotenv
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-4.1-mini
`

The example model uses paid OpenRouter usage. To try a free model, look for an available :free variant with tool calling and copy its full model ID into OPENROUTER_MODEL. [GPT-4.1 Mini on OpenRouter](https://openrouter.ai/openai/gpt-4.1-mini) · [Models that support tools](https://openrouter.ai/models?supported_parameters=tools)

### Direct OpenAI

Create an OpenAI API key and set these values in .env. [OpenAI API keys](https://platform.openai.com/api-keys)

`dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
`

Existing setups without LLM_PROVIDER use OpenAI. Both providers use the openai Python package.

## Test without an API key

`ash
python -m pytest -q
`

## CLI usage

`ash
python llm_file_assistant.py
`

Sample queries:

- Read all resumes in the resumes folder.
- Find resumes mentioning Python experience.
- Read resumes/01_aarav_mehta.pdf and create a summary in output/aarav_summary.md.

## Architecture

ResumeAssistant sends tool definitions to the selected provider, executes requested tools locally through FileTools, and sends the tool results back to the model. Those results can contain extracted resume text or search snippets. OpenRouter can route that content to the provider serving the model. [OpenRouter client tools](https://openrouter.ai/docs/guides/features/tool-calling)

## Scope and limitations

Scanned PDFs (without a selectable text layer) need OCR, which this project does not implement. This is a learning demo, not a production document-processing service. It supports nonrecursive directory listings and literal keyword matching. Use only resumes you are authorized to process.
