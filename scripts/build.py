#!/usr/bin/env python3
"""Build a dependency-free academic homepage from editable JSON files."""
from pathlib import Path
from html import escape
from urllib.parse import urlparse
from itertools import groupby
from datetime import datetime
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
PROFILE = json.loads((ROOT / 'data/profile.json').read_text())
PAPERS = json.loads((ROOT / 'data/publications.json').read_text())
NEWS = json.loads((ROOT / 'data/news.json').read_text())
FIGURES = {p['id']: p for p in json.loads((ROOT / 'data/figure-sources.json').read_text()) if p.get('image')}
e = lambda value: escape(str(value), quote=True)
CATEGORIES = {'3d': '3D vision', 'generation': 'Visual generation', 'restoration': 'Image restoration', 'compression': 'Image compression', 'remote-sensing': 'Remote sensing', 'recognition': 'Recognition & representations', 'detection': 'Object detection', 'perception': 'Visual perception', 'attention': 'Visual representations'}


def url(value):
    parsed = urlparse(value)
    if parsed.scheme not in ('', 'https', 'http', 'mailto') or value.startswith('//'):
        raise ValueError(f'Unsupported URL: {value}')
    return e(value)


def external(href, label, cls=''):
    return f'<a class="{e(cls)}" href="{url(href)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'


def authorship_role(p):
    names = [author.rstrip('*').strip() for author in p['authors']]
    equal = set(p.get('equalContribution', []))
    equal.update(author.rstrip('*').strip() for author in p['authors'] if author.endswith('*'))
    # Equal contribution with the leading author is co-first authorship.
    if PROFILE['name'] in equal and names[0] in equal and len(equal) > 1:
        return 'co-first'
    return 'first' if names[0] == PROFILE['name'] else 'other'


def paper_html(p):
    equal = p.get('equalContribution', [])
    authors = []
    for author in p['authors']:
        name = author.rstrip('*').strip()
        label = e(name)
        if name == PROFILE['name']:
            label = '<strong>' + label + '</strong>'
        if author.endswith('*') or name in equal:
            label += '<sup>*</sup>'
        authors.append(label)
    links = external(p['paper'], 'Paper')
    for field, label in [('code', 'Code'), ('project', 'Project')]:
        if p.get(field):
            links += external(p[field], label)
    if p.get('bibtex'):
        links += f'''<details class="citation"><summary aria-label="BibTeX citation for {e(p['title'])}">BibTeX</summary><div class="citation-panel"><pre>{e(p['bibtex'])}</pre><button type="button" class="copy-button" hidden>Copy citation</button><span class="copy-status" role="status"></span></div></details>'''
    fig = FIGURES.get(p['id'])
    visual = ''
    if fig:
        visual = f'<a class="paper-visual" href="{url(p["paper"])}" target="_blank" rel="noopener noreferrer" aria-label="Read {e(p["title"])}"><img src="{url(fig["image"])}" alt="Figure from {e(p["title"])}" width="{fig["width"]}" height="{fig["height"]}" loading="lazy"></a>'
    else:
        visual = f'<div class="paper-aside" aria-hidden="true"><span>{e(p["venue"])}</span><span>{p["year"]}</span></div>'
    scholar_year = p.get('scholarYear', p['year'])
    date_note = f'<span class="online-year">First listed {scholar_year}</span>' if scholar_year and str(scholar_year) != str(p['year']) else ''
    role = authorship_role(p)
    role_label = {'first': 'First author', 'co-first': 'Co-first author'}.get(role)
    role_tag = f'<span class="author-role">{role_label}</span>' if role_label else ''
    return f'''<article class="paper" data-category="{e(p['category'])}" data-authorship="{role}" id="paper-{e(p['id'])}" aria-labelledby="title-{e(p['id'])}">{visual}<div class="paper-body"><h5 class="paper-title" id="title-{e(p['id'])}"><a href="{url(p['paper'])}" target="_blank" rel="noopener noreferrer">{e(p['title'])}</a></h5><p class="authors">{', '.join(authors)}</p><p class="paper-meta"><span class="venue">{e(p['venue'])}</span><span>{p['year']}</span>{role_tag}{date_note}</p><p class="paper-summary">{e(p.get('summary', ''))}</p><div class="paper-links">{links}</div></div></article>'''


assert PAPERS, 'Add at least one publication'
assert len({p['id'] for p in PAPERS}) == len(PAPERS), 'Duplicate publication IDs'
for p in PAPERS:
    assert re.fullmatch(r'[a-z0-9-]+', p['id']), 'Use URL-safe publication IDs'
    assert p['category'] in CATEGORIES, p['category']
    assert isinstance(p['year'], int)
PAPERS = sorted(PAPERS, key=lambda p: p['year'], reverse=True)
groups = []
for group_id, title in [('lead', 'First / Co-first Author'), ('other', 'Other Co-authored Papers')]:
    group_papers = [p for p in PAPERS if (authorship_role(p) != 'other') == (group_id == 'lead')]
    if not group_papers:
        continue
    years = []
    for year, works in groupby(group_papers, key=lambda p: p['year']):
        year_id = f'year-{group_id}-{year}'
        years.append(f'<section class="year-group" aria-labelledby="{year_id}"><h4 class="year-heading" id="{year_id}">{year}</h4><div class="year-papers">' + ''.join(paper_html(p) for p in works) + '</div></section>')
    groups.append(f'<section class="authorship-group" data-authorship-group="{group_id}" aria-labelledby="authorship-{group_id}"><div class="authorship-heading"><h3 id="authorship-{group_id}">{title}</h3><span class="authorship-count">{len(group_papers)} papers</span></div>' + ''.join(years) + '</section>')
papers_by_id = {p['id']: p for p in PAPERS}
news_rows = []
for item in sorted(NEWS, key=lambda item: item['date'], reverse=True):
    datetime.strptime(item['date'], '%Y-%m')
    assert item['paperIds'] and len(set(item['paperIds'])) == len(item['paperIds'])
    assert item.get('sources'), 'Acceptance news needs a source for its date'
    news_links = [external(papers_by_id[pid]['paper'], item['labels'][pid]) for pid in item['paperIds']]
    paper_links = news_links[0] if len(news_links) == 1 else ', '.join(news_links[:-1]) + ' and ' + news_links[-1]
    count = len(news_links)
    subject = 'One paper' if count == 1 else ('Two papers' if count == 2 else f'{count} papers')
    verb = 'is' if count == 1 else 'are'
    news_rows.append(f'<li><time datetime="{item["date"]}">[{item["date"]}]</time><span>{subject} {paper_links} {verb} accepted to {e(item["venue"])}.</span></li>')
news_html = '<section class="news" id="news" aria-labelledby="news-title"><h2 id="news-title">News</h2><ul class="news-list">' + ''.join(news_rows) + '</ul></section>' if NEWS else ''
news_nav = '<a href="#news">News</a>' if NEWS else ''
links = ''
if PROFILE.get('email'):
    links += f'<a href="mailto:{e(PROFILE["email"])}">Email</a>'
links += external(PROFILE['scholar'], 'Google Scholar') + external(PROFILE['github'], 'GitHub')
if PROFILE.get('cv'):
    links += external(PROFILE['cv'], 'CV')
biography_links = {
    PROFILE[name_key]: PROFILE[url_key]
    for name_key, url_key in [('group', 'groupUrl'), ('institution', 'institutionUrl'), ('advisorName', 'advisorUrl')]
    if PROFILE.get(name_key) and PROFILE.get(url_key)
}
if biography_links:
    pattern = '(' + '|'.join(re.escape(name) for name in sorted(biography_links, key=len, reverse=True)) + ')'
    biography = ''.join(external(biography_links[part], part) if part in biography_links else e(part)
                        for part in re.split(pattern, PROFILE['biography']))
else:
    biography = e(PROFILE['biography'])
portrait = f'<img class="portrait" src="{url(PROFILE["photo"])}" alt="{e(PROFILE["name"])}" width="256" height="256">' if PROFILE.get('photo') else ''
options = '<option value="all">All research areas</option>'
for key, label in CATEGORIES.items():
    if any(p['category'] == key for p in PAPERS):
        options += f'<option value="{key}">{label}</option>'
description = f'{PROFILE["name"]}, Ph.D. student at UESTC. Publications and research in computer vision, image restoration, and 3D vision.'
schema = {'@context': 'https://schema.org', '@type': 'Person', 'name': PROFILE['name'], 'jobTitle': PROFILE['role'], 'affiliation': {'@type': 'Organization', 'name': PROFILE['institution']}, 'sameAs': [PROFILE['scholar'], PROFILE['github']]}
canonical = ''
if PROFILE.get('siteUrl'):
    schema['url'] = PROFILE['siteUrl']
    canonical = f'<link rel="canonical" href="{url(PROFILE["siteUrl"])}"><meta property="og:url" content="{url(PROFILE["siteUrl"])}">'
jsonld = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
equal_note = '<span>* Equal contribution.</span>' if any(p.get('equalContribution') or any(a.endswith('*') for a in p['authors']) for p in PAPERS) else ''
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(PROFILE['name'])} | UESTC</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#fdfdfb"><meta property="og:title" content="{e(PROFILE['name'])} | UESTC"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">{canonical}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script type="application/ld+json">{jsonld}</script></head>
<body id="top"><a class="skip-link" href="#main">Skip to content</a><header class="header container"><a class="brand" href="#top">{e(PROFILE['name'])}</a><nav aria-label="Main navigation"><a href="#about">About</a>{news_nav}<a href="#publications">Publications</a><a href="mailto:{e(PROFILE['email'])}">Email</a></nav></header>
<main id="main" class="container"><section class="about" id="about" aria-labelledby="name"><div class="about-copy"><h1 id="name">{e(PROFILE['name'])}</h1><p class="affiliation">{e(PROFILE['role'])} · <a href="{url(PROFILE['institutionUrl'])}" target="_blank" rel="noopener noreferrer">{e(PROFILE['institutionShort'])}</a></p><p class="bio">{biography}</p><div class="profile-links">{links}</div></div>{portrait}</section>
{news_html}<section class="publications" id="publications" aria-labelledby="publications-title"><div class="section-top"><h2 id="publications-title">Publications</h2><a class="scholar-link" href="{url(PROFILE['scholar'])}" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a></div><div class="publication-toolbar"><p class="publication-note">Grouped by authorship, then by year. {equal_note}</p><label class="topic-control" hidden><span class="sr-only">Filter publications by research area</span><select id="topic-filter">{options}</select></label></div><p class="result-count" id="result-count" role="status">{len(PAPERS)} papers</p><div id="publication-list">{''.join(groups)}</div><p id="empty-state" hidden>No publications in this research area.</p></section>
</main><footer class="container"><span>{e(PROFILE['name'])} · {e(PROFILE['institutionShort'])}</span><span>Updated {e(PROFILE['updated'])}</span><a href="#top">Back to top ↑</a></footer></body></html>'''
OUT.mkdir(exist_ok=True)
(OUT / 'index.html').write_text(html, encoding='utf-8')
(OUT / '.nojekyll').touch()
(OUT / 'publications.bib').write_text('\n\n'.join(p['bibtex'] for p in PAPERS if p.get('bibtex')) + '\n')
if PROFILE.get('siteUrl'):
    (OUT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{e(PROFILE["siteUrl"])}</loc></url></urlset>')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {PROFILE["siteUrl"].rstrip("/")}/sitemap.xml\n')
else:
    (OUT / 'sitemap.xml').unlink(missing_ok=True)
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
# The user site publishes main / (root). Keep a root entry with paths pointing
# at the same assets, while dist remains independently previewable/exportable.
root_html = html.replace('href="assets/', 'href="dist/assets/').replace('src="assets/', 'src="dist/assets/')
(ROOT / 'index.html').write_text(root_html, encoding='utf-8')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text((OUT / 'robots.txt').read_text())
if (OUT / 'sitemap.xml').exists():
    (ROOT / 'sitemap.xml').write_text((OUT / 'sitemap.xml').read_text())
else:
    (ROOT / 'sitemap.xml').unlink(missing_ok=True)
sources = '# Content sources\n\nVerified 2026-11-04.\n\n'
sources += '- Google Scholar exact profile: https://scholar.google.com/citations?user=CsVTBJoAAAAJ&hl=en&pagesize=100\n'
sources += '- Complete snapshot: 18 article rows, “Articles 1–18”, Show more disabled. The profile was retrieved through the configured proxy after a direct timeout.\n'
sources += '- All Scholar entries are retained, including preprints and journal extensions. Formal venue year is used for grouping; original Scholar title, year, venue, and citation ID are retained in the data.\n'
sources += '- Identity/group: https://github.com/gitlonglong. User confirmed PhD student at UESTC, GitHub gitlonglong, and public email lwsch5940@163.com.\n'
sources += '- User confirmed advisor Shuhang Gu: https://shuhanggu.github.io/. The group website https://diggers.ai/ is linked by UESTC’s official article https://news.uestc.edu.cn/info/1005/38639.htm.\n'
sources += '- Portrait is the photo from the user-supplied Scholar profile. Figure sources below are the authors’ official repositories.\n'
sources += '- Descriptions are original summaries. Equal contribution is only marked when supported by Scholar or the authors’ repository. No citation statistics are reproduced.\n'
sources += '- BibTeX omits unverified volume, page, and DOI fields.\n\n'
sources += '- Authorship groups use author order and verified equal-contribution marks; co-first authors share the leading author’s contribution group.\n\n'
sources += '## Acceptance news\n\n'
for item in NEWS:
    sources += f'- {item["date"]} / {item["venue"]} / {", ".join(item["paperIds"])}: {item["evidenceNote"]}\n'
    sources += ''.join(f'  - {source}\n' for source in item['sources'])
sources += '\n'
for p in PAPERS:
    sources += f'## {p["title"]}\n\n' + '\n'.join(f'- {s}' for s in p['sources']) + '\n'
    if p['id'] in FIGURES:
        sources += f'- Figure: {FIGURES[p["id"]]["source"]}\n'
    sources += '\n'
(ROOT / 'SOURCES.md').write_text(sources)
print(f'Built {OUT / "index.html"} with {len(PAPERS)} publications.')
