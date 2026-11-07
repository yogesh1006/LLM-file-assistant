"""Safe local file tools for TXT, PDF, and DOCX resumes.

All paths resolve inside one configured workspace. PDF OCR is not supported.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader

READABLE = {'.txt', '.pdf', '.docx', '.md'}
WRITABLE = {'.txt', '.md'}
MAX_FILE_BYTES = 5 * 1024 * 1024


class FileTools:
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _path(self, filepath: str) -> Path:
        if not isinstance(filepath, str) or not filepath.strip():
            raise ValueError('A nonempty file path is required')
        candidate = (self.workspace / filepath).resolve()
        if not candidate.is_relative_to(self.workspace):
            raise ValueError('Path must remain inside the workspace')
        return candidate

    @staticmethod
    def _metadata(path: Path) -> dict:
        stat = path.stat()
        return {'name': path.name, 'size_bytes': stat.st_size,
                'modified_utc': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                'extension': path.suffix.lower()}

    def read_file(self, filepath: str) -> dict:
        try:
            path = self._path(filepath)
            if path.suffix.lower() not in READABLE:
                raise ValueError('Only .pdf, .txt, .md, and .docx files can be read')
            if not path.is_file():
                raise FileNotFoundError(f'File not found: {filepath}')
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError('File exceeds the 5 MB size limit')
            if path.suffix.lower() in {'.txt', '.md'}:
                content = path.read_text(encoding='utf-8-sig')
            elif path.suffix.lower() == '.docx':
                doc = Document(path)
                paragraphs = [p.text for p in doc.paragraphs]
                table_lines = [' | '.join(cell.text for cell in row.cells)
                               for table in doc.tables for row in table.rows]
                content = '\n'.join(line for line in paragraphs + table_lines if line.strip())
            else:
                reader = PdfReader(str(path))
                if reader.is_encrypted:
                    raise ValueError('Encrypted PDFs are not supported')
                content = '\n'.join(page.extract_text() or '' for page in reader.pages)
                if not content.strip():
                    raise ValueError('No selectable text found; scanned PDFs need OCR')
            return {'success': True, 'filepath': str(path.relative_to(self.workspace)),
                    'content': content, 'metadata': self._metadata(path)}
        except Exception as exc:  # Normalize document-parser failures to structured errors
            return {'success': False, 'filepath': filepath, 'error': str(exc)}

    def list_files(self, directory: str, extension: str | None = None) -> list:
        try:
            path = self._path(directory or '.')
            if not path.is_dir():
                raise NotADirectoryError(f'Directory not found: {directory}')
            if extension:
                extension = extension.lower()
                if not extension.startswith('.'):
                    extension = '.' + extension
            return [{**self._metadata(file), 'filepath': str(file.relative_to(self.workspace))}
                    for file in sorted(path.iterdir())
                    if file.is_file() and not file.is_symlink()
                    and (extension is None or file.suffix.lower() == extension)]
        except (OSError, ValueError) as exc:
            return [{'success': False, 'error': str(exc)}]

    def write_file(self, filepath: str, content: str) -> dict:
        try:
            path = self._path(filepath)
            if path.suffix.lower() not in WRITABLE:
                raise ValueError('Only .txt or .md output files may be written')
            if not isinstance(content, str):
                raise ValueError('Content must be text')
            if len(content.encode('utf-8')) > MAX_FILE_BYTES:
                raise ValueError('Content exceeds the 5 MB size limit')
            if path.exists():
                raise FileExistsError('Refusing to overwrite an existing file')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8') as handle:
                handle.write(content)
            return {'success': True, 'filepath': str(path.relative_to(self.workspace)),
                    'metadata': self._metadata(path)}
        except (OSError, ValueError) as exc:
            return {'success': False, 'filepath': filepath, 'error': str(exc)}

    def search_in_file(self, filepath: str, keyword: str) -> dict:
        result = self.read_file(filepath)
        if not result['success']:
            return result
        if not isinstance(keyword, str) or not keyword.strip():
            return {'success': False, 'filepath': filepath, 'error': 'Keyword must not be empty'}
        text = result['content']
        matches = []
        for match in re.finditer(re.escape(keyword), text, flags=re.IGNORECASE):
            start, end = match.span()
            matches.append({'start': start, 'end': end, 'match': text[start:end],
                            'context': text[max(0, start - 70):min(len(text), end + 70)].replace('\n', ' ')})
            if len(matches) >= 100:
                break
        return {'success': True, 'filepath': result['filepath'], 'keyword': keyword,
                'match_count': len(matches), 'matches': matches}


_default = FileTools(Path(__file__).resolve().parent)


def read_file(filepath: str) -> dict:
    return _default.read_file(filepath)


def list_files(directory: str, extension: str | None = None) -> list:
    return _default.list_files(directory, extension)


def write_file(filepath: str, content: str) -> dict:
    return _default.write_file(filepath, content)


def search_in_file(filepath: str, keyword: str) -> dict:
    return _default.search_in_file(filepath, keyword)
