import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('control', Path(__file__).resolve().parents[1] / 'control.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


class ControllerTests(unittest.TestCase):
    def test_start_keeps_paths_as_arguments_and_preserves_session_environment(self):
        with tempfile.TemporaryDirectory(prefix='ipad host ') as directory:
            root = Path(directory)
            with patch.object(control, 'backend', return_value=root), \
                 patch.object(control, 'status', return_value={'ready': True}), \
                 patch.object(control, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as run, \
                 patch.dict(control.os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test-instance'}):
                control.start('extend', 'software')
            argv = run.call_args.args[0]
            self.assertIn(str(root / 'scripts/native.py'), argv)
            self.assertIn('--setenv=HYPRLAND_INSTANCE_SIGNATURE=test-instance', argv)
            self.assertIn('--property=KillMode=mixed', argv)
            self.assertEqual(argv[-4:], ['--mode', 'extend', '--encoder', 'software'])

    def test_start_refuses_to_replace_an_existing_session(self):
        for existing in ('running', 'external'):
            with self.subTest(existing=existing), patch.object(control, 'backend'), \
                 patch.object(control, 'status', return_value={'ready': True, existing: True}), \
                 patch.object(control, 'run') as run:
                with self.assertRaises(ValueError):
                    control.start('mirror', 'vaapi')
                run.assert_not_called()

    def test_other_usb_device_does_not_make_selected_ipad_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / '.runtime'
            runtime.mkdir()
            (runtime / 'device.json').write_text(json.dumps({'udid': 'selected', 'model': 'pro97'}))
            (runtime / 'receiver-token').write_text('token')
            with patch.object(control, 'backend', return_value=root), \
                 patch.object(control, 'unit_state', return_value={'ActiveState': 'inactive'}), \
                 patch.object(control, 'run', return_value=subprocess.CompletedProcess([], 0, 'other\n', '')):
                state = control.status()
            self.assertFalse(state['ready'])
            self.assertFalse(state['connected'])
            self.assertNotIn('udid', state)


if __name__ == '__main__':
    unittest.main()
