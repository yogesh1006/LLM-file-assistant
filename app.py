"""Streamlit chat app. Every browser session has an isolated temporary workspace."""
import os
from pathlib import Path
import shutil
import tempfile
import uuid

import streamlit as st
from llm_file_assistant import ResumeAssistant

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title='Resume File Assistant', page_icon='📄')
st.title('📄 LLM Resume File Assistant')
st.caption('Explore dummy resumes and uploaded PDF, DOCX, and TXT files using OpenAI tool calling.')

if 'workspace' not in st.session_state:
    path = Path(tempfile.mkdtemp(prefix='resume_assistant_'))
    (path / 'resumes').mkdir()
    (path / 'output').mkdir()
    for file in (BASE / 'resumes').iterdir():
        if file.is_file():
            shutil.copy2(file, path / 'resumes' / file.name)
    st.session_state.workspace = str(path)
if 'messages' not in st.session_state:
    st.session_state.messages = []

uploads = st.file_uploader('Upload resumes (up to 5 MB each)', type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
for upload in uploads or []:
    if upload.size > 5 * 1024 * 1024:
        st.error(f'{upload.name} exceeds the 5 MB limit')
        continue
    safe_name = Path(upload.name).name
    if Path(safe_name).suffix.lower() not in {'.pdf', '.docx', '.txt'}:
        continue
    destination = Path(st.session_state.workspace) / 'resumes' / safe_name
    if not destination.exists():
        destination.write_bytes(upload.getvalue())
        st.success(f'Uploaded {safe_name}')

for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])
        if msg.get('logs'):
            with st.expander('Tool calls'):
                st.json(msg['logs'])

question = st.chat_input('Example: Find resumes mentioning Python')
if question:
    st.session_state.messages.append({'role': 'user', 'content': question})
    with st.chat_message('user'):
        st.write(question)
    with st.chat_message('assistant'):
        try:
            assistant = ResumeAssistant(workspace=st.session_state.workspace)
            answer, logs = assistant.ask(question)
            st.write(answer)
            with st.expander('Tool calls', expanded=True):
                st.json(logs)
            st.session_state.messages.append({'role': 'assistant', 'content': answer, 'logs': logs})
        except Exception as exc:
            st.error(f'Unable to process request: {exc}')

st.subheader('Generated summaries')
for file in sorted((Path(st.session_state.workspace) / 'output').glob('*')):
    if file.is_file() and file.suffix.lower() in {'.txt', '.md'}:
        st.download_button(f'Download {file.name}', file.read_bytes(), file_name=file.name,
                           mime='text/plain', key=f'dl_{file.name}')
