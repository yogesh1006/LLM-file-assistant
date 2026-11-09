import json
from types import SimpleNamespace

import httpx
import pytest
from openai import OpenAI

from llm_file_assistant import ResumeAssistant

class FakeClient:
    def __init__(self):
        self.calls = 0
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls += 1
        assert kwargs['store'] is False
        if self.calls == 1:
            call = SimpleNamespace(type='function_call', name='list_files',
                                   arguments='{"directory":"resumes","extension":null}', call_id='id-1')
            return SimpleNamespace(output=[call], output_text='')
        assert any(isinstance(i, dict) and i.get('type') == 'function_call_output' for i in kwargs['input'])
        return SimpleNamespace(output=[], output_text='Found the resumes.')

def test_openai_tool_call_loop(tmp_path, monkeypatch):
    monkeypatch.delenv('LLM_PROVIDER', raising=False)
    (tmp_path / 'resumes').mkdir()
    (tmp_path / 'resumes/a.txt').write_text('Python')
    answer, log = ResumeAssistant(tmp_path, FakeClient()).ask('List resumes')
    assert answer == 'Found the resumes.'
    assert log[0]['tool'] == 'list_files'
    assert log[0]['result'][0]['name'] == 'a.txt'

def test_unknown_tool(tmp_path):
    assistant = ResumeAssistant(tmp_path, FakeClient(), provider='openai')
    assert assistant._execute('delete_file', {})['success'] is False


def test_openrouter_tool_call_loop(tmp_path, monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'openrouter')
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-openrouter-key')
    monkeypatch.setenv('OPENROUTER_MODEL', 'example/tool-model')
    monkeypatch.setenv('OPENAI_API_KEY', 'different-test-key')
    monkeypatch.setenv('OPENAI_BASE_URL', 'https://example.invalid/v1')
    (tmp_path / 'resumes').mkdir()
    (tmp_path / 'resumes/a.txt').write_text('Python developer', encoding='utf-8')

    def tool_call(call_id, name, arguments):
        return {'id': call_id, 'type': 'function',
                'function': {'name': name, 'arguments': json.dumps(arguments)}}

    reasoning = [{'type': 'reasoning.encrypted', 'data': 'opaque-test-value'}]
    first_calls = [tool_call('list-1', 'list_files', {'directory': 'resumes', 'extension': None}),
                   tool_call('search-1', 'search_in_file', {'filepath': 'resumes/a.txt', 'keyword': 'python'}),
                   tool_call('invalid-1', 'read_file', ['not an object']),
                   tool_call('invalid-2', 'list_files', {'directory': 'resumes', 'extension': 123})]
    replies = iter([
        {'tool_calls': first_calls, 'reasoning_details': reasoning, 'reasoning': 'Redundant test text'},
        {'tool_calls': [tool_call('read-1', 'read_file', {'filepath': 'resumes/a.txt'})],
         'reasoning': 'Inspect the selected resume'},
        {'tool_calls': [tool_call('write-1', 'write_file', {'filepath': 'output/a.md', 'content': 'Python developer'})]},
        {'content': 'Summary saved.'},
    ])
    requests = []

    def respond(request):
        assert str(request.url) == 'https://openrouter.ai/api/v1/chat/completions'
        assert request.headers['authorization'] == 'Bearer test-openrouter-key'
        body = json.loads(request.content)
        assert body['model'] == 'example/tool-model'
        assert body['provider'] == {'require_parameters': True}
        assert {tool['function']['name'] for tool in body['tools']} == {
            'list_files', 'search_in_file', 'read_file', 'write_file'}
        assert body['messages'][0]['role'] == 'system'
        assert body['messages'][1] == {'role': 'user', 'content': 'Find Python resumes and save a summary'}
        requests.append(body['messages'])
        reply = next(replies)
        return httpx.Response(200, json={
            'id': 'completion-1', 'object': 'chat.completion', 'created': 0, 'model': body['model'],
            'choices': [{'index': 0, 'finish_reason': 'tool_calls' if 'tool_calls' in reply else 'stop',
                         'message': {'role': 'assistant', **reply}}],
        })

    with httpx.Client(transport=httpx.MockTransport(respond)) as http_client:
        monkeypatch.setattr('openai.OpenAI', lambda **kwargs: OpenAI(http_client=http_client, **kwargs))
        answer, log = ResumeAssistant(tmp_path).ask('Find Python resumes and save a summary')

    assert answer == 'Summary saved.'
    assert len(requests) == 4
    assert requests[1][2] == {'role': 'assistant', 'tool_calls': first_calls, 'reasoning_details': reasoning}
    assert requests[2][-2]['reasoning'] == 'Inspect the selected resume'
    results = [message for message in requests[-1] if message['role'] == 'tool']
    assert [message['tool_call_id'] for message in results] == [
        'list-1', 'search-1', 'invalid-1', 'invalid-2', 'read-1', 'write-1']
    assert [json.loads(message['content']) for message in results] == [entry['result'] for entry in log]
    assert log[0]['result'][0]['name'] == 'a.txt'
    assert log[1]['result']['match_count'] == 1
    assert log[2]['result']['success'] is False
    assert log[3]['result']['success'] is False
    assert log[4]['result']['content'] == 'Python developer'
    assert (tmp_path / 'output/a.md').read_text(encoding='utf-8') == 'Python developer'


@pytest.mark.parametrize('provider, default_model', [('openai', 'gpt-4.1-mini'),
                                                    ('openrouter', 'openai/gpt-4.1-mini')])
def test_provider_requires_its_own_key(tmp_path, monkeypatch, provider, default_model):
    monkeypatch.setenv('LLM_PROVIDER', 'openai' if provider == 'openrouter' else 'openrouter')
    monkeypatch.setenv('OPENAI_API_KEY', 'test-openai-key')
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-openrouter-key')
    key_name = f'{provider.upper()}_API_KEY'
    monkeypatch.delenv(key_name)
    monkeypatch.delenv(f'{provider.upper()}_MODEL', raising=False)

    assistant = ResumeAssistant(tmp_path, provider=provider)
    assert assistant.model == default_model
    assert ResumeAssistant(tmp_path, provider=provider, model='custom-model').model == 'custom-model'
    with pytest.raises(RuntimeError, match=key_name):
        assistant.ask('List resumes')


def test_unknown_provider(tmp_path, monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'unknown')
    with pytest.raises(ValueError, match='LLM_PROVIDER'):
        ResumeAssistant(tmp_path)
