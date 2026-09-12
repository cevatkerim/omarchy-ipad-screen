#!/usr/bin/env python3
"""Local bridge between the Omarchy widget and an installed iPad Screen checkout."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'ipad-screen/host.json'
UNIT = 'ipad-screen.service'


def run(argv, **kwargs):
    return subprocess.run(argv, text=True, capture_output=True, timeout=20, **kwargs)


def backend(path=None):
    root = Path(path).expanduser().resolve() if path else Path(json.loads(CONFIG.read_text())['backend'])
    for file in ('scripts/native.py', 'scripts/ipad.py', 'scripts/install-app.py'):
        if not (root / file).is_file():
            raise ValueError('Choose an iPad Screen checkout containing scripts/native.py')
    return root


def unit_state():
    result = run(['systemctl', '--user', 'show', UNIT,
                  '--property=ActiveState,SubState,Result'])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Cannot contact the user service manager')
    return dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)


def busy(root):
    runtime = root / '.runtime'
    if not runtime.exists():
        return False
    with (runtime / 'screen.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def status():
    try:
        root = backend()
    except FileNotFoundError:
        return dict(configured=False, message='Set up the host using the plugin README.')
    state = unit_state()
    running = state.get('ActiveState') in ('active', 'activating', 'deactivating')
    runtime = root / '.runtime'
    config = json.loads((runtime / 'device.json').read_text()) if (runtime / 'device.json').exists() else {}
    usb = run(['idevice_id', '-l'])
    if usb.returncode:
        raise RuntimeError(usb.stderr.strip() or 'USB discovery failed')
    connected = bool(config) and config['udid'] in usb.stdout.splitlines()
    token = runtime / config.get('token_file', 'receiver-token')
    external = busy(root) and not running
    message = ('Display session running' if running else
               'Display running in a terminal; stop it there first' if external else
               'Pair an iPad using the setup guide' if not config else
               'Connect the paired iPad by USB' if not connected else
               'Install the companion using the setup guide' if not token.exists() else 'Ready')
    log = runtime / 'plugin-session.log'
    detail = ''
    if log.exists():
        with log.open('rb') as stream:
            stream.seek(max(0, log.stat().st_size - 4096))
            lines = stream.read().decode(errors='replace').splitlines()
        detail = next((line for line in reversed(lines) if line.strip()), '')[:500]
    return dict(configured=True, running=running, external=external,
                connected=connected, ready=connected and token.exists() and not external,
                model=config.get('model', 'pro105'), message=message, detail=detail)


def start(mode, encoder):
    root = backend()
    current = status()
    if current.get('running') or current.get('external'):
        raise ValueError('Stop the current display session before starting another')
    if not current.get('ready'):
        raise ValueError(current['message'])
    # The service owns capture independently of QML reloads and extra monitors.
    command = ['systemd-run', '--user', '--collect', '--unit=' + UNIT,
               '--property=Type=exec', '--property=KillMode=mixed',
               '--property=TimeoutStopSec=20', '--property=UMask=0077',
               '--property=PartOf=graphical-session.target',
               '--property=StandardOutput=append:' + str(root / '.runtime/plugin-session.log'),
               '--property=StandardError=inherit']
    for key in ('WAYLAND_DISPLAY', 'HYPRLAND_INSTANCE_SIGNATURE', 'XDG_RUNTIME_DIR', 'PATH'):
        if key in os.environ:
            command.append('--setenv=' + key + '=' + os.environ[key])
    command += [sys.executable, str(root / 'scripts/native.py'), '--mode', mode, '--encoder', encoder]
    result = run(command)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    config = sub.add_parser('configure')
    config.add_argument('backend')
    sub.add_parser('status')
    launch = sub.add_parser('start')
    launch.add_argument('mode', choices=['extend', 'mirror'])
    launch.add_argument('--encoder', choices=['vaapi', 'software'], default='vaapi')
    sub.add_parser('stop')
    args = parser.parse_args()
    if args.action == 'configure':
        root = backend(args.backend)
        CONFIG.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        CONFIG.write_text(json.dumps({'backend': str(root)}, indent=2) + '\n')
        CONFIG.chmod(0o600)
        print(json.dumps({'message': 'Host configured'}))
    elif args.action == 'status':
        print(json.dumps(status()))
    elif args.action == 'start':
        start(args.mode, args.encoder)
        print(json.dumps({'message': 'Starting display'}))
    else:
        state = unit_state()
        if state.get('ActiveState') in ('active', 'activating', 'deactivating'):
            result = run(['systemctl', '--user', 'stop', UNIT])
            if result.returncode:
                raise RuntimeError(result.stderr.strip())
        print(json.dumps({'message': 'Display stopped'}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({'error': str(exc)}))
        sys.exit(1)
