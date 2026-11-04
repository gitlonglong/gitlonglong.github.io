#!/usr/bin/env python3
"""Check built pages for missing assets, broken anchors, and metadata errors."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
        self.articles = 0
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'img':
            assert 'alt' in a, 'Missing image alternative text'
            assert 'width' in a and 'height' in a, 'Missing image dimensions'
        if tag == 'article':
            self.articles += 1
        if a.get('target') == '_blank':
            assert 'noopener' in a.get('rel', ''), 'Unsafe external target'
        for key in ['href', 'src']:
            if a.get(key):
                self.refs.append(a[key])


page = Page()
html = (DIST / 'index.html').read_text()
page.feed(html)
assert page.lang == 'en'
assert page.articles == len(json.loads((ROOT / 'data/publications.json').read_text()))
snapshot_path = ROOT / 'data/scholar-snapshot.json'
if snapshot_path.exists():
    snapshot = json.loads(snapshot_path.read_text())
    entries = json.loads((ROOT / 'data/publications.json').read_text())
    expected = {p['scholarCitationId'] for p in snapshot['publications']}
    actual = {p.get('scholarCitationId') for p in entries}
    assert expected.issubset(actual), 'Some Scholar publications are missing'
    assert len(actual) == len(entries), 'Duplicate Scholar publications'
for ref in page.refs:
    parsed = urlparse(ref)
    if ref.startswith('#'):
        assert ref[1:] in page.ids, f'Missing anchor: {ref}'
    elif not parsed.scheme and not parsed.netloc:
        target = (DIST / unquote(parsed.path)).resolve()
        assert target.is_relative_to(DIST.resolve()), f'Asset outside dist: {ref}'
        assert target.is_file(), f'Missing local asset: {ref}'
for svg in (DIST / 'assets').glob('*.svg'):
    ET.parse(svg)
assert '<meta name="description"' in html
assert 'application/ld+json' in html
assert 'id="topic-filter"' in html
root_html = (ROOT / 'index.html').read_text()
expected_root = html.replace('href="assets/', 'href="dist/assets/').replace('src="assets/', 'src="dist/assets/')
assert root_html == expected_root, 'Root publication entry differs from dist; run build.py'
root_page = Page()
root_page.feed(root_html)
for ref in root_page.refs:
    parsed = urlparse(ref)
    if not parsed.scheme and not parsed.netloc and parsed.path:
        target = (ROOT / unquote(parsed.path)).resolve()
        assert target.is_relative_to(ROOT.resolve()) and target.is_file(), f'Missing root asset: {ref}'
assert (ROOT / '.nojekyll').is_file(), 'Branch publishing requires .nojekyll'
print(f'PASS: {page.articles} publications; {len(page.refs)} references; all local assets, anchors, SVGs and required metadata.')
