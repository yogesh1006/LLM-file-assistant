# LLM Resume File Assistant

A Python assignment demonstrating four structured file-system tools and OpenAI function calling with CLI and Streamlit interfaces.

## Features
- `fs_tools.py`: `read_file`, `list_files`, `write_file`, `search_in_file`.
- PDF (text-based), DOCX, and TXT resume extraction with metadata and contextual matches.
- Strict workspace-relative paths, file size limit (5 MB), and safe new-file writes (`.txt`/`.md`).
- OpenAI Responses API tool-calling loop with visible execution logs.
- Eight entirely fictional sample resumes and upload support.
- Unit tests and a fake OpenAI client test (no API key needed).

## Quick start (Python 3.11+)

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
```

Create an OpenAI API key at https://platform.openai.com/api-keys and replace the placeholder in `.env`. The OpenAI API has separate usage-based billing from ChatGPT. Never commit the `.env` file.

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
3. In Advanced settings → Secrets, add `OPENAI_API_KEY = "..."` and optionally `OPENAI_MODEL = "gpt-4.1-mini"`.
4. Deploy and test tool calling with fictional sample files. Public apps can incur API usage charges; protect access if necessary.

## Architecture

User → CLI/Streamlit → OpenAI Responses API → tool schema → Python dispatcher → FileTools workspace → tool result → OpenAI answer. Tools execute locally on the server, not in the model. Uploaded files are sent as extracted text to OpenAI when read as context.

## Scope and limitations

Scanned PDFs (without a selectable text layer) need OCR, which this assignment does not implement. This is a learning demo, not a production document-processing service. It supports nonrecursive directory listings and literal keyword matching. Upload only resumes you are authorized to process. Uploads are isolated to browser sessions but do not constitute full tenant-grade security.

## Demo video outline (2–3 minutes)

1. (0:00–0:25) Explain folder structure and four Python tools.
2. (0:25–0:50) Run `pytest -q`.
3. (0:50–1:20) Ask to list resumes and show `list_files` trace.
4. (1:20–1:55) Ask for Python experience and show `search_in_file` trace.
5. (1:55–2:30) Ask for a summary and show `read_file` + `write_file` traces; download result.
6. (2:30–2:45) Mention GitHub and live Streamlit deployment.
