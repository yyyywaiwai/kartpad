#!/usr/bin/env python3
"""Local ownership and action receipts; deliberately does not execute actions."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
from urllib.parse import urlparse


class StateError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(state):
    if not isinstance(state, dict) or state.get('schema') != 1:
        raise StateError('invalid state schema; inspect and repair manually')
    if 'owner' not in state or not isinstance(state.get('actions'), dict):
        raise StateError('invalid state structure; inspect and repair manually')
    owner = state['owner']
    if owner is not None and (not isinstance(owner, dict) or not all(
            nonempty(owner.get(key)) for key in ('token', 'label', 'claimedAt'))):
        raise StateError('invalid owner; inspect and repair manually')
    for key, action in state['actions'].items():
        if not nonempty(key) or not isinstance(action, dict) or not nonempty(action.get('startedAt')):
            raise StateError('invalid action record; inspect and repair manually')
        if action.get('status') not in ('pending', 'complete'):
            raise StateError('invalid action status; inspect and repair manually')
        if action['status'] == 'complete' and (not nonempty(action.get('completedAt')) or
                                             not valid_url(action.get('evidence'))):
            raise StateError('invalid completed action; inspect and repair manually')
    return state


def valid_url(value):
    if not nonempty(value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except ValueError:
        return False


@contextmanager
def locked(directory, create=False):
    if not directory.is_absolute():
        raise StateError('--state-dir must be an absolute shared directory')
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise StateError('state directory does not exist; claim initializes it')
    # The kernel lock serializes file updates only. The persisted token owns work
    # between invocations; neither shell exit nor elapsed time releases that claim.
    with open(directory / 'state.lock', 'a', encoding='utf-8') as lock:
        os.chmod(directory / 'state.lock', 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def read_state(directory):
    path = directory / 'state.json'
    if not path.exists():
        # A lock without a state file can result from interrupted initialization.
        return {'schema': 1, 'owner': None, 'actions': {}}
    try:
        return validate(json.loads(path.read_text(encoding='utf-8')))
    except (ValueError, UnicodeError) as error:
        raise StateError('corrupt state JSON; inspect and repair manually') from error


def write_state(directory, state):
    validate(state)
    write_json(directory / 'state.json', state)


def write_json(path, state):
    """Atomically write a JSON checkpoint while the caller holds its lock."""
    directory = path.parent
    fd, name = tempfile.mkstemp(prefix='.state-', suffix='.json', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(state, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def require_owner(state, token):
    owner = state['owner']
    if owner is None or not secrets.compare_digest(owner['token'], token):
        raise StateError('current owner token required; no mutation performed')


def execute(args):
    directory = Path(args.state_dir)
    with locked(directory, create=args.command == 'claim'):
        state = read_state(directory)
        if args.command == 'status':
            require_owner(state, args.token)
            return state
        if args.command == 'inspect':
            return {'key': args.key, 'action': state['actions'].get(args.key)}
        if args.command == 'claim':
            if state['owner'] is not None:
                raise StateError('already claimed; inspect owner and explicitly reconcile before recovery')
            state['owner'] = {'token': 'run_' + secrets.token_urlsafe(32), 'label': args.owner, 'claimedAt': now()}
            result = {'owner': state['owner']}
        else:
            require_owner(state, args.token)
            if args.command == 'release':
                state['owner'] = None
                result = {'released': True}
            elif args.command == 'recover':
                previous = state['owner']
                state['owner'] = {'token': 'run_' + secrets.token_urlsafe(32), 'label': args.owner, 'claimedAt': now()}
                state['lastRecovery'] = {'previousOwner': previous['label'], 'evidence': args.evidence, 'at': now()}
                result = {'owner': state['owner'], 'recovery': state['lastRecovery']}
            elif args.command == 'begin':
                action = state['actions'].get(args.key)
                if action is not None:
                    return {'key': args.key, 'action': action, 'dispatch': False,
                            'reconciliationRequired': action['status'] == 'pending'}
                action = {'status': 'pending', 'startedAt': now()}
                state['actions'][args.key] = action
                result = {'key': args.key, 'action': action, 'dispatch': True, 'reconciliationRequired': False}
            elif args.command == 'retry':
                action = state['actions'].get(args.key)
                if action is None or action['status'] != 'pending':
                    raise StateError('only an existing pending action can be retried')
                if action['startedAt'] != args.expected_started_at:
                    raise StateError('pending attempt changed; inspect before retrying')
                previous = action['startedAt']
                replacement = now()
                # Keep the compare-and-swap marker distinct even if the clock
                # returns the exact prior microsecond. Never expire a claim.
                if replacement == previous:
                    replacement = (datetime.fromisoformat(replacement) + timedelta(microseconds=1)).isoformat()
                action.update(startedAt=replacement, lastRetry={
                    'previousStartedAt': previous, 'evidence': args.evidence, 'at': replacement})
                result = {'key': args.key, 'action': action, 'dispatch': True, 'reconciliationRequired': False}
            else:  # complete
                action = state['actions'].get(args.key)
                if action is None:
                    raise StateError('action must be begun before completion')
                if action['status'] == 'complete':
                    if action['evidence'] != args.evidence:
                        raise StateError('completed action has different evidence; receipt is immutable')
                    return {'key': args.key, 'action': action, 'alreadyComplete': True}
                action.update(status='complete', completedAt=now(), evidence=args.evidence)
                result = {'key': args.key, 'action': action, 'alreadyComplete': False}
        write_state(directory, state)
        return result


def text_arg(value):
    if not value.strip():
        raise argparse.ArgumentTypeError('must not be blank')
    return value


def url_arg(value):
    if not valid_url(value):
        raise argparse.ArgumentTypeError('must be an http(s) evidence URL')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', required=True, help='absolute shared directory; same path in every worktree')
    commands = parser.add_subparsers(dest='command', required=True)
    status = commands.add_parser('status')
    status.add_argument('--token', required=True, type=text_arg)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('--key', required=True, type=text_arg)
    claim = commands.add_parser('claim')
    claim.add_argument('--owner', required=True, type=text_arg, help='continuing task/run reference')
    for command in ('release', 'recover', 'begin', 'complete', 'retry'):
        sub = commands.add_parser(command)
        sub.add_argument('--token', required=True, type=text_arg)
        if command == 'recover':
            sub.add_argument('--owner', required=True, type=text_arg)
            sub.add_argument('--evidence', required=True, type=text_arg, help='mandatory note documenting checked task/process state and handover')
        if command in ('begin', 'complete', 'retry'):
            sub.add_argument('--key', required=True, type=text_arg)
        if command == 'retry':
            sub.add_argument('--expected-started-at', required=True, type=text_arg)
            sub.add_argument('--evidence', required=True, type=text_arg, help='mandatory note recording verified NOT-posted remote outcome')
        if command == 'complete':
            sub.add_argument('--evidence', required=True, type=url_arg)
    try:
        print(json.dumps(execute(parser.parse_args()), sort_keys=True))
    except (StateError, OSError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
