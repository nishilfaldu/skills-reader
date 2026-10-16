#!/usr/bin/env python3
"""Copy mattpocock/skills into the Fumadocs library and retain source links."""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path, PurePosixPath

SOURCE = Path(os.environ.get('SKILLS_SOURCE', '/tmp/mattpocock-skills'))
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'content/docs'
MAP_FILE = ROOT / 'lib/upstream-paths.json'
COMMIT = os.environ.get('SKILLS_COMMIT', '49dd158d1076134a641b33efb035946536778336')
REPO = 'https://github.com/mattpocock/skills'
GUIDE = [
    '01-install', '02-setup', '03-align', '04-language', '05-spec',
    '06-wayfinder', '07-build', '08-design', '09-ship', '10-shelf',
]
ENGINEERING = [
    'ask-matt', 'setup-matt-pocock-skills', 'grill-with-docs', 'domain-modeling',
    'to-spec', 'to-tickets', 'wayfinder', 'implement', 'implement-spec', 'tdd',
    'diagnosing-bugs', 'codebase-design', 'improve-codebase-architecture', 'prototype',
    'code-review', 'pr', 'retro', 'triage', 'research', 'wizard', 'resolving-merge-conflicts',
]
PRODUCTIVITY = [
    'grill-me', 'grilling', 'handoff', 'teach', 'to-questionnaire', 'wait-what', 'writing-for-agents',
]
ACRONYMS = {
    'adr': 'ADR', 'api': 'API', 'cli': 'CLI', 'html': 'HTML', 'json': 'JSON',
    'md': 'MD', 'pr': 'PR', 'tdd': 'TDD', 'ui': 'UI', 'yaml': 'YAML', 'yml': 'YAML',
}
SMALL = {'a', 'and', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
TEXT_SUFFIXES = {'.md', '.yaml', '.yml', '.sh', '.cjs', '.json'}
SKIP_ROOT = {'CHANGELOG.md', 'package.json', 'package-lock.json', 'README.md', 'LICENSE'}
CODE_LANG = {'.yaml': 'yaml', '.yml': 'yaml', '.sh': 'bash', '.cjs': 'javascript', '.json': 'json'}


def nice_title(slug: str) -> str:
    words = re.split(r'[-_\s.]+', slug)
    titled = []
    for index, word in enumerate(word for word in words if word):
        lower = word.lower()
        if lower in ACRONYMS:
            titled.append(ACRONYMS[lower])
        elif lower == 'matt':
            titled.append('Matt')
        elif lower == 'pocock':
            titled.append('Pocock')
        elif lower == 'github':
            titled.append('GitHub')
        elif lower == 'gitlab':
            titled.append('GitLab')
        elif lower == 'openai':
            titled.append('OpenAI')
        elif index and lower in SMALL:
            titled.append(lower)
        else:
            titled.append(word.capitalize())
    return ' '.join(titled)


def as_mdx(path: PurePosixPath) -> PurePosixPath:
    return path.with_name(path.stem.lower().replace('_', '-') + '.mdx')


def destination(src: PurePosixPath) -> PurePosixPath | None:
    if src.suffix.lower() not in TEXT_SUFFIXES:
        return None
    parts = src.parts
    if parts[0] in {'.github', '.changeset', 'scripts', 'node_modules'}:
        return None
    if len(parts) == 1 and src.name in SKIP_ROOT:
        return None
    if parts[0] == 'docs' and src.suffix == '.md':
        return PurePosixPath('explanations', *parts[1:-1], src.stem + '.mdx')
    if parts[0] == 'skills':
        if src.name == 'README.md' and len(parts) == 3:
            return PurePosixPath('source', parts[1], 'index.mdx')
        if src.name == 'SKILL.md':
            return PurePosixPath('source', *parts[1:-1], 'index.mdx')
        return as_mdx(PurePosixPath('source', *parts[1:]))
    if src == PurePosixPath('GLOSSARY.md'):
        return PurePosixPath('glossary.mdx')
    if src == PurePosixPath('SCOPE.md'):
        return PurePosixPath('scope/index.mdx')
    if parts[0] == '.out-of-scope' and src.suffix == '.md':
        return PurePosixPath('scope/out-of-scope', src.stem.lower() + '.mdx')
    if parts[0] == '.agents' and src.suffix == '.md':
        return PurePosixPath('repo', *tuple(part.lower() for part in parts[1:-1]), src.stem.lower() + '.mdx')
    if src.name in {'AGENTS.md', 'CLAUDE.md'}:
        return PurePosixPath('repo', src.stem.lower() + '.mdx')
    if parts[0] == '.claude-plugin' and src.suffix == '.json':
        return PurePosixPath('repo/claude-plugin', src.stem + '.mdx')
    return None


def split_frontmatter(content: str) -> tuple[str | None, str]:
    if content.startswith('---\n'):
        end = content.find('\n---\n', 4)
        if end >= 0:
            return content[4:end], content[end + 5:].lstrip('\n')
    return None, content


def description_from_frontmatter(frontmatter: str | None) -> str:
    if not frontmatter:
        return ''
    match = re.search(r'^description:\s*(.+)$', frontmatter, re.M)
    if not match:
        return ''
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value.replace('\\"', '"').strip()


def heading_title(body: str) -> str | None:
    match = re.match(r'^# (.+)$', body, re.M)
    if not match:
        return None
    return re.sub(r'[`*]', '', match.group(1)).strip()


def page_title(src: PurePosixPath, body: str) -> str:
    if src.name == 'SKILL.md':
        return heading_title(body) or nice_title(src.parent.name)
    if src.parts[0] == 'docs':
        return nice_title(src.stem)
    if src.name == 'README.md':
        return nice_title(src.parent.name if src.parent.name != '' else src.stem)
    if src.suffix != '.md':
        return src.name
    return heading_title(body) or nice_title(src.stem)


def route_of(target: PurePosixPath) -> str:
    route = str(target.with_suffix(''))
    if route.endswith('/index'):
        route = route[:-6]
    if route == 'index':
        route = ''
    return '/docs' + ('/' + route if route else '')


def rewrite_links(body: str, current: PurePosixPath, destinations: dict[PurePosixPath, PurePosixPath]) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        if url.startswith(('https://', 'http://', 'mailto:', '#', 'data:')):
            return match.group(0)
        path, sep, fragment = url.partition('#')
        if not path:
            return match.group(0)
        resolved = PurePosixPath(__import__('posixpath').normpath(str(current.parent / path)))
        if resolved in destinations:
            return '](' + route_of(destinations[resolved]) + (sep + fragment if sep else '') + ')'
        location = 'tree' if (SOURCE / resolved).is_dir() else 'blob'
        return '](' + REPO + '/' + location + '/' + COMMIT + '/' + str(resolved) + (sep + fragment if sep else '') + ')'
    return re.sub(r'\]\(([^)\s]+)\)', replace, body)


def safe_mdx(body: str) -> str:
    chunks = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]+`)', body)
    for index in range(0, len(chunks), 2):
        chunks[index] = chunks[index].replace('<', '&lt;').replace('{', '&#123;').replace('}', '&#125;')
    return ''.join(chunks)


def write_meta(folder: PurePosixPath, title: str, pages: list[str]) -> None:
    dest = TARGET / folder
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'meta.json').write_text(json.dumps({'title': title, 'pages': pages}, indent=2) + '\n')


def ordered(stems: list[str], preferred: list[str]) -> list[str]:
    rank = {name: index for index, name in enumerate(preferred)}
    return sorted(stems, key=lambda stem: (rank.get(stem, len(preferred)), stem))


def main() -> None:
    for generated in ('explanations', 'source', 'scope', 'repo'):
        path = TARGET / generated
        if path.exists():
            shutil.rmtree(path)
    glossary = TARGET / 'glossary.mdx'
    if glossary.exists():
        glossary.unlink()

    files = sorted(
        path for path in SOURCE.rglob('*')
        if path.is_file() and destination(PurePosixPath(path.relative_to(SOURCE).as_posix())) is not None
    )
    destinations: dict[PurePosixPath, PurePosixPath] = {}
    for path in files:
        relative = PurePosixPath(path.relative_to(SOURCE).as_posix())
        target = destination(relative)
        if target is not None:
            destinations[relative] = target

    titles: dict[PurePosixPath, str] = {}
    upstream: dict[str, str] = {}
    for source, target in destinations.items():
        raw = (SOURCE / source).read_text()
        if source.suffix == '.md':
            frontmatter, body = split_frontmatter(raw)
            title = page_title(source, body)
            description = description_from_frontmatter(frontmatter)
            if source.name == 'SKILL.md':
                body = re.sub(r'^# [^\n]+\n+', '', body, count=1)
                if description:
                    body = description + '\n\n' + body
            elif re.match(r'^# ', body):
                body = re.sub(r'^# [^\n]+\n+', '', body, count=1)
            body = rewrite_links(body, source, destinations)
            body = safe_mdx(body)
        else:
            title = page_title(source, raw)
            description = ''
            language = CODE_LANG.get(source.suffix, '')
            body = '```' + language + '\n' + raw.rstrip() + '\n```\n'
        body = re.sub(r'[ \t]+$', '', body, flags=re.M).rstrip() + '\n'
        source_url = REPO + '/blob/' + COMMIT + '/' + str(source)
        body += '\nSource: [`' + str(source) + '`](' + source_url + ')\n'
        document = '---\ntitle: ' + json.dumps(title) + '\n'
        if description:
            document += 'description: ' + json.dumps(description) + '\n'
        document += '---\n\n' + body
        output = TARGET / target
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document)
        titles[source] = title
        route = route_of(target).removeprefix('/docs').strip('/')
        upstream[route] = str(source)

    def stems(folder: str) -> list[str]:
        return sorted(
            path.stem for path in destinations
            if path.parts[:2] == ('docs', folder) and path.suffix == '.md'
        )

    engineering = ordered(stems('engineering'), ENGINEERING)
    productivity = ordered(stems('productivity'), PRODUCTIVITY)
    unknown = [f'engineering/{n}' for n in engineering if n not in ENGINEERING]
    unknown += [f'productivity/{n}' for n in productivity if n not in PRODUCTIVITY]
    for name in unknown:
        print(f'::warning title=Unknown upstream skill::{name} is not in the ordering list in scripts/sync-content.py; it was appended alphabetically')
    (ROOT / '.unknown-skills').write_text(''.join(n + '\n' for n in unknown))
    agents = stems('agents')
    write_meta(PurePosixPath('explanations'), 'Explanations', ['index', 'engineering', 'productivity', 'agents'])
    (TARGET / 'explanations/index.mdx').write_text(
        '---\ntitle: "Explanations"\n---\n\n'
        'These are the human-facing pages from `docs/` in the skills repository. Engineering and productivity skills each have one. The guide links here when you want the full account of a skill.\n\n'
        '- [Engineering](/docs/explanations/engineering)\n'
        '- [Productivity](/docs/explanations/productivity)\n'
        '- [Triage labels](/docs/explanations/agents/triage-labels)\n'
    )
    def explanation_index(folder: str, title: str, pages: list[str]) -> None:
        links = '\n'.join(
            '- [' + nice_title(page) + '](/docs/explanations/' + folder + '/' + page + ')'
            for page in pages
        )
        (TARGET / 'explanations' / folder / 'index.mdx').write_text(
            '---\ntitle: ' + json.dumps(title) + '\n---\n\n' + links + '\n'
        )
        write_meta(PurePosixPath('explanations') / folder, title, ['index', *pages])
    explanation_index('engineering', 'Engineering', engineering)
    explanation_index('productivity', 'Productivity', productivity)
    explanation_index('agents', 'Agents', agents)

    buckets = sorted({path.parts[1] for path in destinations if path.parts[0] == 'skills'})
    write_meta(PurePosixPath('source'), 'Source', ['index', *buckets])
    bucket_links = '\n'.join('- [' + nice_title(bucket) + '](/docs/source/' + bucket + ')' for bucket in buckets)
    (TARGET / 'source/index.mdx').write_text(
        '---\ntitle: "Source"\n---\n\n'
        'The skill files from `skills/`, including each `SKILL.md` and the notes that sit beside it.\n\n'
        + bucket_links + '\n'
    )
    for bucket in buckets:
        skills = sorted({
            path.parts[2] for path in destinations
            if path.parts[:2] == ('skills', bucket) and len(path.parts) > 3 and path.name == 'SKILL.md'
        })
        pages = ['index', *skills] if (TARGET / 'source' / bucket / 'index.mdx').exists() else skills
        write_meta(PurePosixPath('source') / bucket, nice_title(bucket), pages)
        for skill in skills:
            skill_dir = TARGET / 'source' / bucket / skill
            pages_for_skill = ['index']
            extras = sorted(item for item in skill_dir.iterdir() if item.name not in {'index.mdx', 'meta.json'})
            for extra in extras:
                if extra.suffix == '.mdx':
                    pages_for_skill.append(extra.stem)
                elif extra.is_dir():
                    nested = ['index'] if (extra / 'index.mdx').exists() else []
                    nested += sorted(child.stem for child in extra.glob('*.mdx') if child.name != 'index.mdx')
                    nested += sorted(child.name for child in extra.iterdir() if child.is_dir())
                    write_meta(PurePosixPath('source') / bucket / skill / extra.name, nice_title(extra.name), nested)
                    pages_for_skill.append(extra.name)
            write_meta(PurePosixPath('source') / bucket / skill, nice_title(skill), pages_for_skill)

    scope_pages = ['index']
    if (TARGET / 'scope/out-of-scope').is_dir():
        out_pages = sorted(path.stem for path in (TARGET / 'scope/out-of-scope').glob('*.mdx'))
        write_meta(PurePosixPath('scope/out-of-scope'), 'Out of scope', out_pages)
        scope_pages.append('out-of-scope')
    write_meta(PurePosixPath('scope'), 'Scope', scope_pages)

    if (TARGET / 'repo').is_dir():
        repo_pages = sorted(path.stem for path in (TARGET / 'repo').glob('*.mdx') if path.name != 'index.mdx')
        for child in sorted(path for path in (TARGET / 'repo').iterdir() if path.is_dir()):
            child_pages = sorted(page.stem for page in child.glob('*.mdx'))
            for nested in sorted(page for page in child.iterdir() if page.is_dir()):
                nested_pages = sorted(page.stem for page in nested.glob('*.mdx'))
                write_meta(PurePosixPath('repo') / child.name / nested.name, nice_title(nested.name), nested_pages)
                child_pages.append(nested.name)
            write_meta(PurePosixPath('repo') / child.name, nice_title(child.name), child_pages)
            repo_pages.append(child.name)
        links = []
        for page in repo_pages:
            if (TARGET / 'repo' / f'{page}.mdx').exists():
                links.append('- [' + nice_title(page) + '](/docs/repo/' + page + ')')
            else:
                for child in sorted((TARGET / 'repo' / page).glob('*.mdx')):
                    links.append('- [' + nice_title(child.stem) + '](/docs/repo/' + page + '/' + child.stem + ')')
        (TARGET / 'repo/index.mdx').write_text('---\ntitle: "Repo notes"\n---\n\n' + '\n'.join(links) + '\n')
        write_meta(PurePosixPath('repo'), 'Repo notes', ['index', *repo_pages])

    root_pages = [
        'index', '---Guide---', *GUIDE, '---Explanations---', 'explanations',
        '---Source---', 'source', 'glossary', 'scope', 'repo', 'about',
    ]
    write_meta(PurePosixPath('.'), 'Skills', root_pages)
    (ROOT / 'lib/upstream.json').write_text(json.dumps({
        'repo': 'mattpocock/skills',
        'commit': COMMIT,
        'url': REPO + '/tree/' + COMMIT,
    }, indent=2) + '\n')
    MAP_FILE.write_text(json.dumps(upstream, indent=2, sort_keys=True) + '\n')
    print(f'Copied {len(files)} source documents.')


if __name__ == '__main__':
    main()
