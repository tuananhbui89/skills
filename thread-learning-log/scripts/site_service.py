#!/usr/bin/env python3
"""Build, verify and serve the local learning website in the user's launchd session."""
import argparse
import hashlib
import sys
import json
import os
import plistlib
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from weekly_config import ROOT, REPORT_DIR, SITE_DIR, PORT
URL = f'http://127.0.0.1:{PORT}'


def service_label(root):
    return 'local.thread-learning-log.' + hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:12]


def health(url=URL):
    request = urllib.request.Request(url + '/site-data.json', headers={'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('Port is occupied by another service; it was left unchanged') from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, ConnectionRefusedError):
            return None
        raise RuntimeError(f'Cannot verify local website: {error.reason}') from error
    except (ValueError, TimeoutError) as error:
        raise RuntimeError('Port is occupied by another service or an unresponsive server; it was left unchanged') from error
    if not isinstance(data, dict) or data.get('appId') != 'personal-learning-log':
        raise RuntimeError('Port is occupied by another service; it was left unchanged')
    return data


def ensure(root=ROOT, report_dir=REPORT_DIR, week=None):
    site = SITE_DIR
    label = service_label(root)
    environment = {**os.environ, 'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:' + os.environ.get('PATH', ''), 'LEARNING_LOG_ROOT': str(root), 'LEARNING_LOG_REPORT_DIR': str(report_dir), 'LEARNING_LOG_WEEKLY_DIR': str(report_dir / 'weeks')}
    node = shutil.which('node', path=environment['PATH'])
    if not node or not (site / 'node_modules/vite/bin/vite.js').exists():
        raise RuntimeError('Install website dependencies before running the scheduled review')
    result = subprocess.run([node, '--experimental-strip-types', './scripts/build-content.ts'], cwd=site, env=environment, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Website build failed; last valid data retained: ' + result.stderr[-2000:])
    expected = json.loads((site / 'public/site-data.json').read_text())
    if week and week not in expected.get('weeks', {}):
        raise RuntimeError(f'Published data is missing requested week {week}')
    current = health()
    reused = current is not None
    if current is None:
        if sys.platform != 'darwin':
            raise RuntimeError('Automatic background start requires macOS; start the bundled site with npm run dev using the configured paths and port')
        state = root / '.personal-memory/site-service'
        state.mkdir(parents=True, exist_ok=True)
        plist = state / (label + '.plist')
        config = {'Label': label, 'ProgramArguments': [node, str(site / 'node_modules/vite/bin/vite.js'), '--host', '127.0.0.1', '--port', str(PORT), '--strictPort'], 'WorkingDirectory': str(site), 'RunAtLoad': True, 'KeepAlive': False,
                  'EnvironmentVariables': {'PATH': environment['PATH'], 'LEARNING_LOG_ROOT': str(root), 'LEARNING_LOG_REPORT_DIR': str(report_dir), 'LEARNING_LOG_WEEKLY_DIR': str(report_dir / 'weeks'), 'LEARNING_LOG_PORT': str(PORT)},
                  'StandardOutPath': str(state / 'stdout.log'), 'StandardErrorPath': str(state / 'stderr.log')}
        plist.write_bytes(plistlib.dumps(config))
        domain = f'gui/{os.getuid()}'
        target = domain + '/' + label
        present = subprocess.run(['/bin/launchctl', 'print', target], capture_output=True).returncode == 0
        command = ['/bin/launchctl', 'kickstart', target] if present else ['/bin/launchctl', 'bootstrap', domain, str(plist)]
        launched = subprocess.run(command, capture_output=True, text=True)
        if launched.returncode:
            raise RuntimeError('Unable to start local site: ' + (launched.stderr or launched.stdout).strip())
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        current = health()
        if current is not None and current.get('weeks') == expected.get('weeks') and current.get('entries') == expected.get('entries'):
            return {'url': URL, 'week': week, 'reused_server': reused, 'verified': True, 'lesson_count': len(current.get('entries', {}))}
        time.sleep(.5)
    raise RuntimeError('Local site did not serve the published dataset within 30 seconds; inspect .personal-memory/site-service/stderr.log')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['ensure', 'status', 'stop'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--report-dir', type=Path, default=REPORT_DIR)
    parser.add_argument('--week-start')
    args = parser.parse_args()
    if args.command == 'ensure':
        print(json.dumps(ensure(args.root, args.report_dir, args.week_start)))
    elif args.command == 'status':
        data = health()
        print(json.dumps({'url': URL, 'running': data is not None, 'weeks': sorted(data.get('weeks', {})) if data else []}))
    else:
        result = subprocess.run(['/bin/launchctl', 'bootout', f'gui/{os.getuid()}/{service_label(args.root)}'], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('No owned launchd service could be stopped: ' + result.stderr.strip())
        print('Stopped the learning-log launchd service.')

if __name__ == '__main__':
    main()
