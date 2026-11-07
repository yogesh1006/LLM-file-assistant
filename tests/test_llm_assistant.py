from types import SimpleNamespace
from llm_file_assistant import ResumeAssistant

class FakeClient:
    def __init__(self):
        self.calls = 0
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            call = SimpleNamespace(type='function_call', name='list_files',
                                   arguments='{"directory":"resumes","extension":null}', call_id='id-1')
            return SimpleNamespace(output=[call], output_text='')
        assert any(isinstance(i, dict) and i.get('type') == 'function_call_output' for i in kwargs['input'])
        return SimpleNamespace(output=[], output_text='Found the resumes.')

def test_tool_call_loop(tmp_path):
    (tmp_path / 'resumes').mkdir()
    (tmp_path / 'resumes/a.txt').write_text('Python')
    answer, log = ResumeAssistant(tmp_path, FakeClient()).ask('List resumes')
    assert answer == 'Found the resumes.'
    assert log[0]['tool'] == 'list_files'
    assert log[0]['result'][0]['name'] == 'a.txt'

def test_unknown_tool(tmp_path):
    assistant = ResumeAssistant(tmp_path, FakeClient())
    assert assistant._execute('delete_file', {})['success'] is False
