"""Dependency-free source metadata and relative documentation link checks."""
from pathlib import Path
from urllib.parse import unquote
import json
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
skip = {'.git', '.gradle', 'build', 'dist', '.cxx', '.kotlin', '.toolchain', '__pycache__', 'private'}
checked = 0
for path in root.rglob('*'):
    relative = path.relative_to(root)
    if any(part in skip for part in relative.parts) or not path.is_file():
        continue
    if path.name == 'local.properties' or path.name.endswith('.local.json'):
        continue
    if path.suffix not in {'.md', '.json', '.xml'}:
        continue
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.json': json.loads(text)
    if path.suffix == '.xml': ET.fromstring(text)
    if path.suffix == '.md':
        for link in re.findall(r'\]\(([^)]+)\)', text):
            link = link.split('#', 1)[0]
            if not link or re.match(r'^[a-z]+:', link, re.I): continue
            destination = (path.parent / unquote(link)).resolve()
            assert destination.is_relative_to(root), 'Documentation link escapes repository'
            assert destination.exists(), f'Missing relative link: {relative} -> {link}'
    checked += 1
print(f'Checked {checked} Markdown/JSON/XML files. Android runtime validation is separate.')
