import importlib.util
import os
os.environ["LEARNING_LOG_TIMEZONE"] = "Australia/Melbourne"
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import append_learning_log as writer


class WeeklyTests(unittest.TestCase):
    def module(self):
        path = SCRIPTS / 'weekly_review.py'
        self.assertTrue(path.exists(), 'Weekly review CLI must exist')
        spec = importlib.util.spec_from_file_location('weekly_review', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def fixture(self):
        evidence = {'thread_id': 'chat-1', 'title': 'Source chat', 'at': '2026-11-18T00:00:00Z', 'line': 12}
        return {'week_start': '2026-11-16', 'coverage': {'thread_count': 1, 'archived_count': 0, 'limitations': []},
                'tasks': [{'id': 'shipped', 'title': 'Ship parser', 'project': 'Demo', 'status': 'completed', 'summary': 'Parser passed validation.', 'evidence': [evidence], 'lesson_keys': ['validate-boundaries']}],
                'lessons': [{'concept_key': 'validate-boundaries', 'title': 'Validate time boundaries', 'primary_tag': '@Testing', 'tags': ['@Testing'], 'category': 'debugging', 'confidence': .9, 'usefulness_score': 3, 'evidence': [evidence], 'sections': {'Summary': 'Convert calendar boundaries before filtering.', 'What I Learned': 'Use local calendar arithmetic before converting to UTC.'}}]}

    def test_writer_repeated_entry_does_not_duplicate_or_lose_manual_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log.md'
            path.write_text('# Learning Log\n\nManual introduction.\n')
            entry = '## 2026-11-18 | @Testing | Lesson\n\nentry_id: "stable"\n\n### Summary\nHello\n'
            writer.append_entry(path, entry)
            before = path.read_bytes()
            writer.append_entry(path, entry)
            self.assertEqual(path.read_bytes(), before)
            self.assertIn('Manual introduction.', path.read_text())

    def test_melbourne_calendar_window_handles_dst(self):
        mod = self.module()
        start, end = mod.week_bounds('2027-03-29')
        self.assertEqual((end.timestamp() - start.timestamp()) / 3600, 169)
        self.assertEqual(mod.previous_week(datetime.fromisoformat('2026-11-23T09:00:00+11:00')), '2026-11-16')

    def test_scan_uses_message_times_and_includes_archives(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'archived_sessions').mkdir()
            (root / 'session_index.jsonl').write_text(json.dumps({'id': 'old-chat', 'thread_name': 'Old chat'}) + '\n')
            records = [{'type': 'session_meta', 'payload': {'id': 'old-chat', 'cwd': '/demo', 'source': 'cli'}}]
            for stamp, phase, text in [('2026-11-15T12:59:59Z', 'final_answer', 'Before'), ('2026-11-15T13:00:00Z', 'final_answer', 'Within'), ('2026-11-18T00:00:00Z', 'analysis', 'Hidden'), ('2026-11-22T13:00:00Z', 'final_answer', 'After')]:
                records.append({'timestamp': stamp, 'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'phase': phase, 'content': [{'type': 'output_text', 'text': text}]}})
            (root / 'archived_sessions' / 'old.jsonl').write_text('\n'.join(json.dumps(r) for r in records))
            data = mod.scan_history(root, '2026-11-16', [])
            self.assertEqual(data['coverage']['archived_count'], 1)
            self.assertEqual([m['text'] for m in data['threads'][0]['messages']], ['Within'])

    def test_publish_rerun_and_cross_week_lesson_reuse(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'learning-log.md').write_text('# Learning Log\n\nKeep this introduction.\n')
            report = root / 'reports'
            first = mod.publish(self.fixture(), root, report)
            before = (root / 'learning-log.md').read_bytes()
            mod.publish(self.fixture(), root, report)
            self.assertEqual((root / 'learning-log.md').read_bytes(), before)
            self.assertEqual(len(first['lesson_ids']), 1)
            payload = self.fixture()
            payload['week_start'] = '2026-11-23'
            payload['tasks'][0]['evidence'][0]['at'] = '2026-11-24T00:00:00Z'
            payload['lessons'][0]['evidence'][0]['at'] = '2026-11-24T00:00:00Z'
            second = mod.publish(payload, root, report)
            self.assertEqual(first['lesson_ids'], second['lesson_ids'])
            self.assertEqual(second.get('lesson_evidence', {}).get(second['lesson_ids'][0], [{}])[0].get('at'), '2026-11-24T00:00:00Z')
            self.assertEqual((root / 'learning-log.md').read_bytes(), before)
            self.assertEqual((report / 'weekly-progress.md').read_text().count('## Week of'), 2)

    def test_low_confidence_omitted_invalid_status_rejected_before_writes(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = self.fixture()
            payload['lessons'][0]['confidence'] = .5
            result = mod.publish(payload, root, root / 'reports')
            self.assertEqual(result['lesson_ids'], [])
            before = (root / 'reports' / 'weeks' / '2026-11-16.json').read_bytes()
            payload['tasks'][0]['status'] = 'maybe'
            with self.assertRaises(ValueError):
                mod.publish(payload, root, root / 'reports')
            self.assertEqual((root / 'reports' / 'weeks' / '2026-11-16.json').read_bytes(), before)

    def test_revisited_manual_lesson_keeps_concept_mapping_across_weeks(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'learning-log.md').write_text('# Learning Log\n\n## 2026-01-01 | @Testing | Existing lesson\n\nentry_id: "manual-1"\ntitle: "Existing lesson"\n\n### Summary\nAlready known.\n')
            payload = self.fixture()
            payload['lessons'][0]['existing_entry_id'] = 'manual-1'
            mod.publish(payload, root, root / 'reports')
            payload['week_start'] = '2026-11-23'
            payload['tasks'][0]['evidence'][0]['at'] = '2026-11-24T00:00:00Z'
            payload['lessons'][0]['evidence'][0]['at'] = '2026-11-24T00:00:00Z'
            del payload['lessons'][0]['existing_entry_id']
            result = mod.publish(payload, root, root / 'reports')
            self.assertEqual(result['lesson_ids'], ['manual-1'])

    def test_publication_recovers_after_report_write_failure(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / 'reports'
            report.mkdir()
            from unittest.mock import patch
            real_write = mod.atomic_write
            def fail_report(path, text):
                if path.name == 'weekly-progress.md':
                    raise OSError('Simulated disk failure after lesson append')
                return real_write(path, text)
            with patch.object(mod, 'atomic_write', fail_report), self.assertRaises(OSError):
                mod.publish(self.fixture(), root, report)
            self.assertEqual((root / 'learning-log.md').read_text().count('entry_id:'), 1)
            mod.publish(self.fixture(), root, report)
            self.assertEqual((root / 'learning-log.md').read_text().count('entry_id:'), 1)


if __name__ == '__main__':
    unittest.main()
