from pathlib import Path
import pytest
from fs_tools import FileTools

@pytest.fixture
def files(tmp_path):
    (tmp_path / 'resumes').mkdir()
    (tmp_path / 'resumes' / 'one.txt').write_text('Python and React. python developer.', encoding='utf-8')
    return FileTools(tmp_path)

def test_read_txt(files):
    res = files.read_file('resumes/one.txt')
    assert res['success'] and 'Python' in res['content']
    assert res['metadata']['size_bytes'] > 0

def test_list_with_filter(files):
    assert len(files.list_files('resumes', '.txt')) == 1
    assert len(files.list_files('resumes', '.pdf')) == 0

def test_search_case_insensitive(files):
    res = files.search_in_file('resumes/one.txt', 'PYTHON')
    assert res['success'] and res['match_count'] == 2
    assert all('context' in match for match in res['matches'])

def test_write_creates_directory_and_refuses_overwrite(files):
    assert files.write_file('output/sub/summary.md', 'Summary')['success']
    assert not files.write_file('output/sub/summary.md', 'Changed')['success']
    assert files.read_file('output/sub/summary.md')['success'] is True
    assert (files.workspace / 'output/sub/summary.md').read_text() == 'Summary'

def test_missing_and_invalid(files):
    assert not files.read_file('resumes/missing.pdf')['success']
    assert not files.search_in_file('resumes/one.txt', '')['success']
    assert not files.write_file('output/bad.exe', 'x')['success']

def test_traversal_blocked(files):
    assert not files.read_file('../outside.txt')['success']
    assert not files.write_file('../outside.txt', 'x')['success']
    assert files.list_files('../')[0]['success'] is False

def test_pdf_docx(files):
    from reportlab.pdfgen import canvas
    from docx import Document
    p = files.workspace / 'resumes' / 'two.pdf'
    c = canvas.Canvas(str(p)); c.drawString(60, 750, 'Python PDF Resume'); c.save()
    d = Document(); d.add_paragraph('React DOCX Resume'); d.save(files.workspace / 'resumes' / 'three.docx')
    assert 'Python' in files.read_file('resumes/two.pdf')['content']
    assert 'React' in files.read_file('resumes/three.docx')['content']
