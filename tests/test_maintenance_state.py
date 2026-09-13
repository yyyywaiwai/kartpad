"""Exercise persisted ownership and uncertain-action handling through the real CLI."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'maintenance-state.py'


class MaintenanceStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'shared'

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.directory), *args],
                                text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def claim(self, owner='task-A'):
        return self.run_cli('claim', '--owner', owner)['owner']['token']

    def test_generated_tokens_with_leading_dash_are_safe_cli_arguments(self):
        def with_random(value, *args):
            code = ("import runpy, secrets, sys; value=sys.argv[1]; script=sys.argv[2]; "
                    "secrets.token_urlsafe=lambda _: value; sys.argv=sys.argv[2:]; "
                    "runpy.run_path(script, run_name='__main__')")
            result = subprocess.run([sys.executable, '-c', code, value, str(SCRIPT),
                                     '--state-dir', str(self.directory), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)['owner']['token']
        original = with_random('-leading-claim', 'claim', '--owner', 'task-A')
        self.assertEqual(original, 'run_-leading-claim')
        self.run_cli('begin', '--token', original, '--key', 'cli-safe')
        replacement = with_random('-leading-recover', 'recover', '--token', original,
                                  '--owner', 'task-B', '--evidence', 'Verified previous run stopped.')
        self.assertEqual(replacement, 'run_-leading-recover')
        self.run_cli('status', '--token', replacement)
        self.run_cli('release', '--token', replacement)

    def test_competing_claims_have_one_winner(self):
        def claim(index):
            return subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.directory),
                                   'claim', '--owner', f'task-{index}'], capture_output=True, text=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(claim, range(8)))
        winners = [r for r in results if r.returncode == 0]
        self.assertEqual(len(winners), 1)
        winner = json.loads(winners[0].stdout)['owner']
        self.assertEqual(self.run_cli('status', '--token', winner['token'])['owner'], winner)

    def test_shell_exit_does_not_release_owner_and_old_tokens_cannot_mutate(self):
        old = self.claim()
        self.run_cli('claim', '--owner', 'task-B', ok=False)
        self.run_cli('status', '--token', 'wrong-token', ok=False)
        for command in [('begin', '--key', 'x'), ('release',),
                        ('recover', '--owner', 'task-B', '--evidence', 'checked')]:
            self.run_cli(*command, '--token', 'wrong-token', ok=False)
        new = self.run_cli('recover', '--token', old, '--owner', 'task-B',
                           '--evidence', 'Prior task failed; inspected its worktree and found no running build.')['owner']['token']
        self.assertNotEqual(old, new)
        self.run_cli('begin', '--token', old, '--key', 'x', ok=False)
        self.run_cli('release', '--token', old, ok=False)
        self.run_cli('release', '--token', new)
        self.run_cli('begin', '--token', new, '--key', 'x', ok=False)
        self.assertNotEqual(self.claim('task-C'), new)

    def test_pending_action_survives_interrupted_work_and_recovery(self):
        token = self.claim()
        first = self.run_cli('begin', '--token', token, '--key', 'issue123:code63:online')
        self.assertTrue(first['dispatch'])
        # No completion follows: simulate a coordinator dying after the remote
        # operation might have happened. Each CLI invocation is a fresh process.
        new = self.run_cli('recover', '--token', token, '--owner', 'recovery-run',
                           '--evidence', 'Task failed after posting; remote outcome needs inspection.')['owner']['token']
        again = self.run_cli('begin', '--token', new, '--key', 'issue123:code63:online')
        self.assertFalse(again['dispatch'])
        self.assertTrue(again['reconciliationRequired'])
        self.assertEqual(again['action'], first['action'])
        self.run_cli('complete', '--token', token, '--key', 'issue123:code63:online',
                     '--evidence', 'https://github.com/example/repo/issues/123#issuecomment-1', ok=False)

    def test_completed_action_is_deduplicated_and_receipt_immutable(self):
        token = self.claim()
        key = 'issue123:code63:online'
        url = 'https://github.com/example/repo/issues/123#issuecomment-1'
        self.run_cli('begin', '--token', token, '--key', key)
        result = self.run_cli('complete', '--token', token, '--key', key, '--evidence', url)
        self.assertFalse(result['alreadyComplete'])
        self.assertTrue(self.run_cli('complete', '--token', token, '--key', key, '--evidence', url)['alreadyComplete'])
        again = self.run_cli('begin', '--token', token, '--key', key)
        self.assertFalse(again['dispatch'])
        self.assertFalse(again['reconciliationRequired'])
        self.run_cli('complete', '--token', token, '--key', key, '--evidence', url + '2', ok=False)
        self.assertEqual(self.run_cli('inspect', '--key', key)['action']['evidence'], url)
        self.run_cli('release', '--token', token)
        replacement = self.claim('later-run')
        self.assertFalse(self.run_cli('begin', '--token', replacement, '--key', key)['dispatch'])

    def test_concurrent_action_begin_only_dispatches_once(self):
        token = self.claim()
        def begin(_):
            return self.run_cli('begin', '--token', token, '--key', 'same-action')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(begin, range(8)))
        self.assertEqual(sum(r['dispatch'] for r in results), 1)

    def test_explicit_retry_uses_expected_attempt_and_preserves_evidence(self):
        token = self.claim()
        key = 'uncertain-post'
        original = self.run_cli('begin', '--token', token, '--key', key)['action']
        retry_args = ('retry', '--key', key, '--expected-started-at', original['startedAt'])
        self.run_cli(*retry_args, '--token', 'wrong-token', '--evidence', 'Checked remote', ok=False)
        self.run_cli(*retry_args, '--token', token, ok=False)
        self.run_cli(*retry_args, '--token', token, '--evidence', ' ', ok=False)
        self.run_cli('retry', '--token', token, '--key', key, '--expected-started-at', 'old-attempt',
                     '--evidence', 'Checked remote', ok=False)
        self.assertEqual(self.run_cli('inspect', '--key', key)['action'], original)
        note = 'Inspected issue comments and refreshed timeline: no matching post exists.'
        retried = self.run_cli(*retry_args, '--token', token, '--evidence', note)
        self.assertTrue(retried['dispatch'])
        self.assertNotEqual(retried['action']['startedAt'], original['startedAt'])
        self.assertEqual(retried['action']['lastRetry']['evidence'], note)
        self.assertEqual(retried['action']['lastRetry']['previousStartedAt'], original['startedAt'])
        self.run_cli(*retry_args, '--token', token, '--evidence', note, ok=False)
        self.assertFalse(self.run_cli('begin', '--token', token, '--key', key)['dispatch'])
        self.run_cli('complete', '--token', token, '--key', key, '--evidence', 'https://example.com/comment')
        self.run_cli('retry', '--token', token, '--key', key,
                     '--expected-started-at', retried['action']['startedAt'], '--evidence', note, ok=False)
        self.run_cli('retry', '--token', token, '--key', 'missing',
                     '--expected-started-at', original['startedAt'], '--evidence', note, ok=False)

    def test_competing_retries_dispatch_only_one_new_attempt(self):
        token = self.claim()
        original = self.run_cli('begin', '--token', token, '--key', 'shared-retry')['action']
        def retry(_):
            return subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.directory),
                                   'retry', '--token', token, '--key', 'shared-retry',
                                   '--expected-started-at', original['startedAt'],
                                   '--evidence', 'Remote inspection confirmed no post exists.'],
                                  capture_output=True, text=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(retry, range(8)))
        winners = [r for r in results if r.returncode == 0]
        self.assertEqual(len(winners), 1)
        self.assertTrue(json.loads(winners[0].stdout)['dispatch'])
        self.assertEqual(self.run_cli('inspect', '--key', 'shared-retry')['action'],
                         json.loads(winners[0].stdout)['action'])

    def test_corruption_fails_closed_without_replacing_state(self):
        token = self.claim()
        path = self.directory / 'state.json'
        for bad in ('{broken', '{}', '{"schema":1,"owner":{},"actions":{}}',
                    '{"schema":1,"owner":null,"actions":{"x":{"status":"complete","startedAt":"now"}}}'):
            path.write_text(bad)
            for args in [('status', '--token', token), ('claim', '--owner', 'other'),
                         ('recover', '--token', token, '--owner', 'other', '--evidence', 'checked')]:
                self.run_cli(*args, ok=False)
                self.assertEqual(path.read_text(), bad)

    def test_missing_recovery_evidence_or_action_evidence_is_rejected(self):
        token = self.claim()
        self.run_cli('recover', '--token', token, '--owner', 'other', ok=False)
        self.run_cli('recover', '--token', token, '--owner', 'other', '--evidence', ' ', ok=False)
        self.run_cli('complete', '--token', token, '--key', 'unknown', '--evidence', 'https://example.com/test', ok=False)
        self.run_cli('begin', '--token', token, '--key', 'action')
        self.run_cli('complete', '--token', token, '--key', 'action', '--evidence', 'not-a-url', ok=False)
        self.assertEqual(self.run_cli('inspect', '--key', 'action')['action']['status'], 'pending')

    def test_shared_directory_is_explicit_and_absolute(self):
        for prefix in ([], ['--state-dir', 'relative']):
            result = subprocess.run([sys.executable, str(SCRIPT), *prefix, 'claim', '--owner', 'test'],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
