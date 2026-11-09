# LLM Resume File Assistant

A Python assignment demonstrating four structured file-system tools with OpenAI or OpenRouter, through a CLI and a Streamlit app.

## Features

- `fs_tools.py`: `read_file`, `list_files`, `write_file`, `search_in_file`.
- PDF (text-based), DOCX, and TXT resume extraction with metadata and contextual matches.
- Strict workspace-relative paths, file size limit (5 MB), and safe new-file writes (`.txt`/`.md`).
- OpenAI Responses and OpenRouter Chat Completions with visible tool execution logs.
- Eight entirely fictional sample resumes and upload support.
- Offline tests for both providers and all four file tools.

## Quick start (Python 3.11+)

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

If you already have a `.env`, edit it in place. Keep `.env` out of version control.

### OpenRouter

Create a key and set these values in `.env`. [OpenRouter API keys](https://openrouter.ai/keys)

```dotenv
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-4.1-mini
```

The app sets the OpenRouter endpoint and uses the OpenRouter key for both the CLI and Streamlit. The example model uses paid OpenRouter usage. To try a free model, look for an available `:free` variant with tool calling and copy its full model ID into `OPENROUTER_MODEL`. [GPT-4.1 Mini on OpenRouter](https://openrouter.ai/openai/gpt-4.1-mini) · [Models that support tools](https://openrouter.ai/models?supported_parameters=tools)

### Direct OpenAI

Create an OpenAI API key and set these values in `.env`. [OpenAI API keys](https://platform.openai.com/api-keys)

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
```

Existing setups without `LLM_PROVIDER` use OpenAI. Restart the CLI or Streamlit after changing `.env`. Both providers use the `openai` Python package.

## Test without an API key

```bash
python -m pytest -q
```

## CLI

```bash
python llm_file_assistant.py
```

Sample queries:

- `Read all resumes in the resumes folder.`
- `Find resumes mentioning Python experience.`
- `Read resumes/01_aarav_mehta.pdf and create a summary in output/aarav_summary.md.`

## Streamlit UI

```bash
streamlit run app.py
```

Each UI session gets a temporary workspace with separate files. Upload `.pdf`, `.docx`, or `.txt` resumes, ask questions, view tool traces, and download output summaries. Files may be deleted when the app restarts.

## Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub **without** `.env` or actual private resumes.
2. Visit https://share.streamlit.io, choose Create app, select the repository and `app.py`.
3. In Advanced settings → Secrets, add the selected provider's settings at the top level. For OpenRouter, use the example below. For direct OpenAI, use `LLM_PROVIDER = "openai"`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL`.
4. Deploy and test tool calling with fictional sample files. Public apps can incur API usage charges; protect access if necessary.

```toml
LLM_PROVIDER = "openrouter"
OPENROUTER_API_KEY = "your_openrouter_key"
OPENROUTER_MODEL = "openai/gpt-4.1-mini"
```

## Architecture

The CLI and Streamlit share `ResumeAssistant`. It sends tool definitions to the selected provider, executes requested tools locally through `FileTools`, and sends the tool results back to the model. Those results can contain extracted resume text or search snippets. OpenRouter can route that content to the provider serving the model. [OpenRouter client tools](https://openrouter.ai/docs/guides/features/tool-calling)

## Scope and limitations

Scanned PDFs (without a selectable text layer) need OCR, which this assignment does not implement. This is a learning demo, not a production document-processing service. It supports nonrecursive directory listings and literal keyword matching. Upload only resumes you are authorized to process. Uploads are isolated to browser sessions but do not constitute full tenant-grade security.

## Demo video outline (2–3 minutes)

1. (0:00–0:25) Explain folder structure and four Python tools.
2. (0:25–0:50) Run `pytest -q`.
3. (0:50–1:20) Ask to list resumes and show `list_files` trace.
4. (1:20–1:55) Ask for Python experience and show `search_in_file` trace.
5. (1:55–2:30) Ask for a summary and show `read_file` + `write_file` traces; download result.
6. (2:30–2:45) Mention GitHub and live Streamlit deployment.
