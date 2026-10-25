"""Refresh only the compact project block; keep all artwork/copy intact.

One bounded public-repository request, at most six displayed projects. On an
error, README.md stays unchanged. Optional GITHUB_TOKEN is never logged.
"""
import argparse
import html
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
START, END = '<!-- PROJECTS:START -->', '<!-- PROJECTS:END -->'
BYTE_LIMIT = 2 * 1024 * 1024


def clean(value, limit=110):
    value = re.sub(r'\s+', ' ', str(value or '')).strip()
    if len(value) > limit:
        value = value[:limit-1].rsplit(' ', 1)[0] + '…'
    return html.escape(value).replace('[', '&#91;').replace(']', '&#93;')


def asset_image(path, width, height, label):
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to((ROOT / 'assets').resolve()) or not resolved.is_file():
        raise ValueError('Project artwork must be an existing local asset')
    return f'<img src="{html.escape(path, quote=True)}" width="{int(width)}" height="{int(height)}" alt="{html.escape(label, quote=True)}" title="{html.escape(label, quote=True)}">'


def render_projects(config, repos):
    owner = config['owner']
    if not re.fullmatch(r'[A-Za-z0-9-]+', owner):
        raise ValueError('Invalid owner')
    excluded = {name.lower() for name in config['exclude']}
    featured = [name.lower() for name in config['featured']]
    eligible = [repo for repo in repos
                if repo.get('owner', {}).get('login', '').lower() == owner.lower()
                and not repo.get('private') and not repo.get('fork')
                and not repo.get('archived') and not repo.get('disabled')
                and repo['name'].lower() not in excluded
                and (config['auto_discover'] or repo['name'].lower() in featured)]
    eligible.sort(key=lambda repo: (featured.index(repo['name'].lower()) if repo['name'].lower() in featured else len(featured),
                                   -int(re.sub(r'\D', '', repo.get('pushed_at') or '0'))))
    count = min(max(int(config['max_projects']), 1), 6)
    rows = []
    for repo in eligible[:count]:
        name = repo['name']
        url = 'https://github.com/' + owner + '/' + urllib.parse.quote(name, safe='')
        override = config['overrides'].get(name, {})
        title = f'**[{clean(name, 70)}]({url})**'
        if override.get('badge'):
            badge = override['badge']
            title = f'<a href="{url}">' + asset_image(badge['src'], badge['width'], badge['height'], name) + '</a>'
        if repo.get('language'):
            language_icon = config.get('language_icons', {}).get(repo['language'])
            if language_icon:
                title += ' ' + asset_image(language_icon, 26, 26, repo['language'])
            else:
                title += ' · <sub>' + clean(repo['language'], 30) + '</sub>'
        for link in override.get('links', []):
            parsed = urllib.parse.urlsplit(link['url'])
            if parsed.scheme != 'https' or not parsed.netloc:
                raise ValueError('Project links must use HTTPS')
            safe_url = link['url'].replace('(', '%28').replace(')', '%29')
            if link.get('badge'):
                badge = link['badge']
                title += f' <a href="{html.escape(safe_url, quote=True)}">' + asset_image(badge['src'], badge['width'], badge['height'], link['label']) + '</a>'
            else:
                title += f" · [{clean(link['label'], 24)}]({safe_url})"
        description = clean(override.get('description') or repo.get('description'))
        rows.append(title + ('<br>' + description if description else ''))
    if not rows:
        raise ValueError('No public projects found; keeping the existing block')
    if len(eligible) > count:
        rows.append(f'<sub>[More repositories](https://github.com/{owner}?tab=repositories)</sub>')
    return '\n\n'.join(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-json', type=Path, help='Use a saved public API response for review')
    parser.add_argument('--save-json', type=Path, help='Save the public API response outside the README')
    args = parser.parse_args()
    config = json.loads((ROOT / 'projects.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'[A-Za-z0-9-]+', config['owner']):
        raise ValueError('Invalid owner')
    current = (ROOT / 'README.md').read_text(encoding='utf-8')
    if current.count(START) != 1 or current.count(END) != 1:
        raise ValueError('Expected exactly one project block')
    if args.from_json:
        repos = json.loads(args.from_json.read_text(encoding='utf-8'))
    else:
        url = f"https://api.github.com/users/{config['owner']}/repos?per_page=100&type=owner&sort=pushed"
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ember-profile-projects'}
        if os.environ.get('GITHUB_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as response:
            body = response.read(BYTE_LIMIT + 1)
        if len(body) > BYTE_LIMIT:
            raise ValueError('Repository response exceeded the byte limit')
        repos = json.loads(body)
    if not isinstance(repos, list) or len(repos) > 100:
        raise ValueError('Unexpected repository response')
    generated = render_projects(config, repos)
    before, rest = current.split(START)
    _, after = rest.split(END)
    updated = before + START + '\n' + generated + '\n' + END + after
    if updated != current:
        (ROOT / 'README.md').write_text(updated, encoding='utf-8', newline='\n')
    if args.save_json:
        args.save_json.write_text(json.dumps(repos, indent=2), encoding='utf-8')
    print('Project block refreshed.' if updated != current else 'Project block unchanged.')


if __name__ == '__main__':
    main()
