#!/usr/bin/env python3
"""Build a standalone preview and a portable source archive beside this project."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import base64
import mimetypes
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], check=True)
subprocess.run([sys.executable, str(ROOT / 'scripts/check.py')], check=True)
html = (ROOT / 'dist/index.html').read_text()
html = html.replace('<link rel="stylesheet" href="assets/site.css">', '<style>' + (ROOT / 'dist/assets/site.css').read_text() + '</style>')
html = html.replace('<script src="assets/site.js" defer></script>', '')
html = html.replace('</body>', '<script>' + (ROOT / 'dist/assets/site.js').read_text() + '</script></body>')
for ref in set(re.findall(r'(?:src|href)="(assets/[^\"]+|publications\.bib)"', html)):
    path = ROOT / 'dist' / ref
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    data = base64.b64encode(path.read_bytes()).decode()
    html = html.replace('"' + ref + '"', '"data:' + mime + ';base64,' + data + '"')
preview = ROOT.parent / 'wei-long-preview.html'
preview.write_text(html)
archive = ROOT.parent / 'academic-homepage.zip'
with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        relative = p.relative_to(ROOT)
        if p.is_file() and not any(part in {'.git', '.openai', '__pycache__', '.sites-runtime'} for part in relative.parts):
            z.write(p, Path('academic-homepage') / relative)
    z.write(preview, preview.name)
print(f'Preview: {preview}\nSource archive: {archive}')
