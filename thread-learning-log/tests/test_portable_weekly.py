import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'

class PortableWeeklyTests(unittest.TestCase):
    def test_configured_paths_timezone_and_cold_site_location(self):
        self.assertTrue((SCRIPTS / 'weekly_review.py').exists(), 'Weekly workflow must be included')
        with tempfile.TemporaryDirectory() as tmp:
            environment = {**os.environ, 'LEARNING_LOG_ROOT': tmp + '/notes', 'LEARNING_LOG_REPORT_DIR': tmp + '/reports', 'LEARNING_LOG_TIMEZONE': 'America/New_York', 'LEARNING_LOG_PORT': '4188'}
            code = "import json, weekly_review as w, append_learning_log as a, site_service as s; from datetime import datetime; start,end=w.week_bounds('2026-03-02');print(json.dumps({'root':str(w.ROOT),'report':str(w.REPORT_DIR),'log':str(a.DEFAULT_LOG_PATH),'zone':w.TZ.key,'hours':(end.timestamp()-start.timestamp())/3600,'url':s.URL,'site':str(s.SITE_DIR),'previous':w.previous_week(datetime.fromisoformat('2026-03-09T09:00:00-04:00'))}))"
            result=subprocess.run([sys.executable,'-c',code],cwd=SCRIPTS,env=environment,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout)
            self.assertEqual(data['root'],str((Path(tmp)/'notes').resolve())); self.assertEqual(data['report'],str((Path(tmp)/'reports').resolve()))
            self.assertEqual(data['log'],str((Path(tmp)/'notes/learning-log.md').resolve()));self.assertEqual(data['zone'],'America/New_York')
            self.assertEqual(data['hours'],167);self.assertEqual(data['previous'],'2026-03-02')
            self.assertEqual(data['url'],'http://127.0.0.1:4188')
            self.assertEqual(Path(data['site']),SCRIPTS.parent/'assets/learning-log-site')

    def test_install_does_not_require_or_change_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);config=home/'config.toml';config.write_text('model = "example-model"\n')
            result=subprocess.run([sys.executable,str(SCRIPTS/'install_global_skill.py'),'--codex-home',tmp],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(config.read_text(),'model = "example-model"\n')
            self.assertTrue((home/'skills/thread-learning-log/SKILL.md').is_file())

    def test_install_excludes_private_data_and_dependencies(self):
        spec=importlib.util.spec_from_file_location('installer',SCRIPTS/'install_global_skill.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';dest=Path(tmp)/'installed';source.mkdir();(source/'SKILL.md').write_text('public instructions')
            private=['private.sqlite','private.sqlite-wal','private.db','.env.local','learning-log.md','reports/weeks/week.json','.personal-memory/scan.json','assets/learning-log-site/public/site-data.json','assets/learning-log-site/src/generated/site-data.json','assets/learning-log-site/node_modules/demo/index.js','assets/learning-log-site/dist/index.html','.env']
            for name in private:
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('private')
            mod.copy_skill(source,dest,False)
            self.assertEqual(sorted(str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()),['SKILL.md'])

if __name__=='__main__':unittest.main()
