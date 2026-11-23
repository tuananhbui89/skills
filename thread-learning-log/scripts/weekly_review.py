#!/usr/bin/env python3
"""Read weekly Codex evidence and publish reviewed task/lesson snapshots locally."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from append_learning_log import atomic_write, file_lock, normalize_payload, render_entry, append_entry

from weekly_config import ROOT, REPORT_DIR, TZ


def week_bounds(week_start):
    start = datetime.strptime(week_start, '%Y-%m-%d').replace(tzinfo=TZ)
    if start.weekday() != 0:
        raise ValueError('week_start must be a Monday')
    return start, start + timedelta(days=7)


def previous_week(now=None):
    now = (now or datetime.now(TZ)).astimezone(TZ)
    return (now - timedelta(days=now.weekday() + 7)).strftime('%Y-%m-%d')


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else None
    except (ValueError, TypeError):
        return None


def json_records(path, limitations):
    try:
        with path.open(encoding='utf-8', errors='replace') as stream:
            for line, raw in enumerate(stream, 1):
                try:
                    record = json.loads(raw)
                    if isinstance(record, dict):
                        yield line, record
                except ValueError:
                    limitations.append(f'Malformed record: {path.name}:{line}')
    except OSError as error:
        limitations.append(f'Unreadable history: {path.name}: {error.strerror}')


def scan_history(home, week_start, exclude):
    start, end = week_bounds(week_start)
    limitations, indexed, metadata = [], {}, {}
    index = home / 'session_index.jsonl'
    if index.exists():
        for _, item in json_records(index, limitations):
            if item.get('id'):
                indexed[item['id']] = item
    databases = sorted(home.glob('state_*.sqlite'), key=lambda p: int(p.stem.split('_')[-1]), reverse=True)
    for database in databases:
        try:
            with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as connection:
                connection.row_factory = sqlite3.Row
                for row in connection.execute('SELECT * FROM threads'):
                    item = dict(row)
                    if 'subagent' not in str(item.get('source', '')).lower():
                        metadata[item['id']] = item
            break
        except sqlite3.Error as error:
            limitations.append(f'History metadata unavailable: {database.name}: {error}')
    paths = {}
    for folder in ('sessions', 'archived_sessions'):
        for path in (home / folder).rglob('*.jsonl'):
            try:
                with path.open(encoding='utf-8') as handle:
                    header = json.loads(handle.readline())
                meta = header.get('payload', {})
                tid = meta.get('id')
                if not tid or tid in exclude or 'subagent' in str(meta.get('source', '')).lower():
                    continue
                # Indexed human chats, or app-known non-exec chats; ignore orphan exec runs.
                if tid not in indexed and (tid not in metadata or metadata[tid].get('source') == 'exec'):
                    continue
                paths.setdefault(tid, []).append((path, folder == 'archived_sessions', meta))
            except (OSError, ValueError, TypeError):
                limitations.append(f'Unreadable session header: {path.name}')
    threads = []
    for tid, rollouts in paths.items():
        messages = []
        for path, archived, meta in rollouts:
            for line, record in json_records(path, limitations):
                at = timestamp(record.get('timestamp'))
                if not at or not start <= at < end:
                    continue
                payload = record.get('payload', {})
                if not isinstance(payload, dict):
                    continue
                role, phase, text = '', '', ''
                if record.get('type') == 'response_item' and payload.get('type') == 'message':
                    role, phase = payload.get('role'), payload.get('phase', '')
                    content = payload.get('content', [])
                    text = content if isinstance(content, str) else '\n'.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') in ('text', 'input_text', 'output_text'))
                elif record.get('type') == 'event_msg' and payload.get('type') in ('user_message', 'agent_message'):
                    role = 'user' if payload['type'] == 'user_message' else 'assistant'
                    text = payload.get('message') or ''
                if role not in ('user', 'assistant') or phase == 'analysis' or not text.strip():
                    continue
                if text.lstrip().startswith(('<environment_context>', '<skill>', '# AGENTS.md', '<permissions instructions>')):
                    continue
                if '<decision>DONT_NOTIFY</decision>' in text:
                    continue
                duplicate = next((m for m in reversed(messages[-4:]) if m['role'] == role and m['text'] == text and abs((at - timestamp(m['at'])).total_seconds()) < 5), None)
                if duplicate:
                    if phase:
                        duplicate.update(phase=phase, line=line)
                    continue
                messages.append({'at': at.isoformat(), 'line': line, 'role': role, 'phase': phase, 'text': text, 'source_path': str(path)})
        if messages:
            record = metadata.get(tid, {})
            threads.append({'thread_id': tid, 'title': record.get('name') or indexed.get(tid, {}).get('thread_name') or record.get('title') or tid,
                            'cwd': record.get('cwd') or rollouts[0][2].get('cwd', ''), 'archived': bool(record.get('archived') or any(r[1] for r in rollouts)),
                            'messages': sorted(messages, key=lambda m: m['at'])})
    if not paths:
        limitations.append('No readable indexed Codex sessions were found.')
    return {'week_start': week_start, 'week_end': (end - timedelta(days=1)).date().isoformat(), 'timezone': TZ.key,
            'coverage': {'thread_count': len(threads), 'archived_count': sum(t['archived'] for t in threads), 'limitations': list(dict.fromkeys(limitations))}, 'threads': threads}


def lesson_catalog(path):
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    entries = {}
    for block in re.split(r'(?=^## \d{4}-\d{2}-\d{2})', text, flags=re.M):
        meta = {}
        for key, value in re.findall(r'^(entry_id|concept_key|title|date|tags):\s*(.+)$', block, re.M):
            try:
                meta[key] = json.loads(value)
            except ValueError:
                meta[key] = value
        if meta.get('entry_id'):
            match = re.search(r'^### Summary\n(.*?)(?=^### |\Z)', block, re.M | re.S)
            meta['summary'] = match.group(1).strip() if match else ''
            entries[meta['entry_id']] = meta
    return entries


def evidence_refs(values, start, end):
    if not isinstance(values, list) or not values:
        raise ValueError('Every task and lesson requires dated evidence')
    refs = []
    for value in values:
        at = timestamp(value.get('at'))
        tid, title = value.get('thread_id', ''), value.get('title', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', tid) or not title or not at or not start <= at < end:
            raise ValueError('Evidence must identify a source chat and a timestamp inside the week')
        refs.append({**value, 'url': 'codex://threads/' + tid})
    return refs


def normalized_review(payload):
    start, end = week_bounds(payload['week_start'])
    tasks, lessons, ids = [], [], set()
    for task in payload.get('tasks', []):
        if not task.get('id') or task['id'] in ids or task.get('status') not in ('completed', 'in_progress'):
            raise ValueError('Tasks require unique IDs and a completed/in_progress status')
        ids.add(task['id'])
        if not all(isinstance(task.get(k), str) and task[k].strip() for k in ('title', 'project', 'summary')):
            raise ValueError('Tasks require title, project and concise summary')
        tasks.append({**task, 'evidence': evidence_refs(task.get('evidence'), start, end)})
    for lesson in payload.get('lessons', []):
        key = lesson.get('concept_key', '').strip().lower()
        if not re.fullmatch(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', key):
            raise ValueError('Lessons require a stable concept_key')
        confidence, score = float(lesson.get('confidence', 0)), float(lesson.get('usefulness_score', 0))
        if not 0 <= confidence <= 1 or not 0 <= score <= 3:
            raise ValueError('Lesson confidence/score outside valid range')
        refs = evidence_refs(lesson.get('evidence'), start, end)
        if confidence < .8 or score < 2:
            continue
        if not lesson.get('sections', {}).get('What I Learned', '').strip():
            raise ValueError('Lessons require reusable knowledge in What I Learned')
        local = min(timestamp(r['at']) for r in refs).astimezone(TZ)
        entry = normalize_payload({**lesson, 'concept_key': key,
            'entry_id': 'weekly-lesson-' + hashlib.sha256(key.encode()).hexdigest()[:20],
            'date': local.date().isoformat(), 'time_start': local.strftime('%H:%M'), 'time_end': local.strftime('%H:%M'),
            'time_basis': 'inferred', 'source': 'codex-thread-weekly',
            'context_status': lesson.get('context_status', 'partial'), 'source_locations': list(dict.fromkeys(r['url'] for r in refs))})
        lessons.append({'entry': entry, 'evidence': refs, 'existing_entry_id': lesson.get('existing_entry_id')})
    return tasks, lessons, start, end


def md_label(value):
    return str(value).replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')


def render_week(snapshot, catalog):
    lines = [f"## Week of {snapshot['week_start']} to {snapshot['week_end']}", '']
    for task in snapshot['tasks'][:8]:
        source = task['evidence'][0]
        status = 'Completed' if task['status'] == 'completed' else 'In progress'
        lines.append(f"- **{md_label(task['title'])}** ({status}) — {task['summary']} [{md_label(source['title'])}]({source['url']})")
    if not snapshot['tasks']:
        lines.append('No qualifying task activity was found for this week.')
    lines.extend(['', '### Reusable lessons', ''])
    for entry_id in snapshot['lesson_ids']:
        entry = catalog[entry_id]
        lines.append(f"- **{md_label(entry['title'])}** — {entry['summary']}")
    if not snapshot['lesson_ids']:
        lines.append('No new or revisited reusable lessons met the inclusion criteria.')
    lines.extend(['', f"Coverage: {snapshot['coverage'].get('thread_count', 0)} active chats, including {snapshot['coverage'].get('archived_count', 0)} archived."])
    for limitation in snapshot['coverage'].get('limitations', []):
        lines.append(f"- Limitation: {limitation}")
    return '\n'.join(lines).rstrip() + '\n'


def replace_week(text, section, week_start):
    pattern = re.compile(r'^## Week of ' + re.escape(week_start) + r' to \d{4}-\d{2}-\d{2}[^\n]*\n.*?(?=^## |\Z)', re.M | re.S)
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        raise ValueError('Duplicate existing weekly sections require review')
    if matches:
        match = matches[0]
        return text[:match.start()] + section + ('\n' if text[match.end():] else '') + text[match.end():]
    return text + ('' if text.endswith('\n\n') else '\n' if text.endswith('\n') else '\n\n') + section


def publish(payload, root=ROOT, report_dir=REPORT_DIR):
    tasks, lessons, start, end = normalized_review(payload)  # Validate before mutation.
    log = root / 'learning-log.md'
    with file_lock(root / '.personal-memory' / 'weekly-review.lock'):
        catalog = lesson_catalog(log)
        concepts = {entry['concept_key']: entry['entry_id'] for entry in catalog.values() if entry.get('concept_key')}
        for prior_path in sorted((report_dir / 'weeks').glob('*.json')):
            prior_week = json.loads(prior_path.read_text())
            for key, entry_id in prior_week.get('lesson_concepts', {}).items():
                if entry_id in catalog:
                    concepts.setdefault(key, entry_id)
        chosen, keys, additions, lesson_evidence = [], {}, [], {}
        for lesson in lessons:
            entry = lesson['entry']
            explicit = lesson['existing_entry_id']
            if explicit and explicit not in catalog:
                raise ValueError('existing_entry_id does not exist in the learning log')
            entry_id = explicit or concepts.get(entry['concept_key']) or entry['entry_id']
            if entry_id not in catalog:
                additions.append(entry)
                catalog[entry_id] = {**entry, 'summary': entry['sections']['Summary']}
            concepts[entry['concept_key']] = entry_id
            keys[entry['concept_key']] = entry_id
            lesson_evidence.setdefault(entry_id, []).extend(lesson['evidence'])
            if entry_id not in chosen:
                chosen.append(entry_id)
        for task in tasks:
            task['lesson_ids'] = list(dict.fromkeys(keys[k] for k in task.pop('lesson_keys', []) if k in keys))
        snapshot = {'schema_version': 1, 'week_start': start.date().isoformat(), 'week_end': (end - timedelta(days=1)).date().isoformat(),
                    'window_start': start.isoformat(), 'window_end_exclusive': end.isoformat(), 'timezone': TZ.key,
                    'coverage': payload.get('coverage', {'thread_count': 0, 'archived_count': 0, 'limitations': []}),
                    'tasks': tasks, 'lesson_ids': chosen, 'lesson_evidence': lesson_evidence, 'lesson_concepts': keys}
        path = report_dir / 'weeks' / f"{snapshot['week_start']}.json"
        report = report_dir / 'weekly-progress.md'
        old_report = report.read_text(encoding='utf-8') if report.exists() else '# Weekly Codex progress report\n'
        rendered = replace_week(old_report, render_week(snapshot, catalog), snapshot['week_start'])
        prior = json.loads(path.read_text()) if path.exists() else {}
        previous_time = prior.pop('generated_at', None)
        snapshot['generated_at'] = previous_time if prior == snapshot and previous_time else datetime.now(timezone.utc).isoformat()
        # Recovery is repeatable: append_entry protects existing IDs; week files are upserts.
        for entry in additions:
            append_entry(log, render_entry(entry))
        atomic_write(path, json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
        atomic_write(report, rendered)
        if json.loads(path.read_text()) != snapshot or report.read_text() != rendered:
            raise RuntimeError('Saved report verification failed')
        return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan')
    scan.add_argument('--week-start', default=None)
    scan.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    scan.add_argument('--exclude-thread', action='append', default=[])
    scan.add_argument('--output', type=Path, required=True)
    catalog = commands.add_parser('catalog')
    catalog.add_argument('--root', type=Path, default=ROOT)
    pub = commands.add_parser('publish')
    pub.add_argument('--input', type=Path, required=True)
    pub.add_argument('--root', type=Path, default=ROOT)
    pub.add_argument('--report-dir', type=Path, default=REPORT_DIR)
    pub.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'scan':
        data = scan_history(args.codex_home, args.week_start or previous_week(), args.exclude_thread + [os.environ.get('CODEX_THREAD_ID', '')])
        atomic_write(args.output, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'output': str(args.output), 'coverage': data['coverage'], 'week_start': data['week_start']}))
    elif args.command == 'catalog':
        print(json.dumps(lesson_catalog(args.root / 'learning-log.md'), ensure_ascii=False, indent=2))
    else:
        payload = json.loads(args.input.read_text())
        if args.dry_run:
            tasks, lessons, start, _ = normalized_review(payload)
            print(json.dumps({'valid': True, 'week_start': start.date().isoformat(), 'tasks': len(tasks), 'eligible_lessons': len(lessons)}))
        else:
            data = publish(payload, args.root, args.report_dir)
            print(json.dumps({'week_start': data['week_start'], 'tasks': len(data['tasks']), 'lessons': len(data['lesson_ids']), 'report_dir': str(args.report_dir)}))


if __name__ == '__main__':
    main()
