"""Target isolation and display-profile tests; no SDK, device or VM is required."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('emulator', Path(__file__).resolve().parents[1] / 'tools/emulator.py')
emulator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emulator)


class Profiles(unittest.TestCase):
    def test_current_overrides_win_regardless_of_order(self):
        p = emulator.display_profile('Override size: 640x480\nPhysical size: 480x640',
                                     'Override density: 180\nPhysical density: 160', '32', '1.15')
        self.assertEqual((p['width'], p['height'], p['density'], p['fontScale']), (640, 480, 180, 1.15))

    def test_missing_font_setting_uses_android_default(self):
        p = emulator.display_profile('Physical size: 480x640', 'Physical density: 160', '32', 'null')
        self.assertEqual(p['fontScale'], 1.0)

    def test_invalid_or_unrepresentable_profile_is_rejected(self):
        for change in ({'api': 31}, {'width': 0}, {'density': 9999}, {'fontScale': float('nan')}, {'width': '480'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                emulator.validate_profile(emulator.DEFAULT | change)

    def test_capture_rejects_missing_display_data(self):
        with self.assertRaises(ValueError):
            emulator.display_profile('', '', '32', '1')


class Targets(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'toolchain.local.json').write_text(json.dumps({'sdkRoot': str(self.root / 'sdk')}), encoding='utf-8')
        self.lab = emulator.Lab(self.root)
        self.calls = []

    def fake_devices(self, devices, owned=()):
        def execute(args, **kwargs):
            args = [str(value) for value in args]
            self.calls.append(args)
            if args[1:] == ['devices']:
                return devices
            serial = args[2]
            if args[3:] == ['shell', 'getprop', 'ro.kernel.qemu']:
                return '1'
            if args[3:] == ['emu', 'avd', 'name']:
                return (emulator.AVD if serial in owned else 'another_avd') + '\nOK'
            raise AssertionError('Unexpected command')
        self.lab.execute = execute

    def test_physical_offline_and_unrelated_devices_are_not_selected(self):
        self.fake_devices('List of devices attached\nphysical-test device\nemulator-5554 device\nemulator-5556 offline')
        self.assertIsNone(self.lab.target(required=False))
        self.assertFalse(any('physical-test' in call or 'emulator-5556' in call for call in self.calls))

    def test_only_owned_virtual_device_is_selected(self):
        self.fake_devices('emulator-5554 device\nemulator-5556 device', ('emulator-5556',))
        self.assertEqual(self.lab.target(), 'emulator-5556')

    def test_ambiguous_owned_instances_are_rejected(self):
        self.fake_devices('emulator-5554 device\nemulator-5556 device', ('emulator-5554', 'emulator-5556'))
        with self.assertRaises(RuntimeError):
            self.lab.target()

    def test_no_install_or_input_without_verified_lab_target(self):
        self.fake_devices('physical-test device\nemulator-5554 device')
        with self.assertRaises(RuntimeError):
            self.lab.launch('gpt-viewer')
        with self.assertRaises(RuntimeError):
            self.lab.key('enter')
        self.assertFalse(any('install' in call or 'input' in call for call in self.calls))

    def test_qemu_flag_is_required_even_with_matching_avd_name(self):
        self.fake_devices('emulator-5554 device', ('emulator-5554',))
        previous = self.lab.execute
        self.lab.execute = lambda args, **kw: '0' if 'ro.kernel.qemu' in args else previous(args, **kw)
        self.assertIsNone(self.lab.target(required=False))

    def test_capture_is_read_only_and_does_not_store_target_identity(self):
        answers = {('get-state',): 'device', ('shell', 'wm', 'size'): 'Physical size: 480x640',
                   ('shell', 'wm', 'density'): 'Physical density: 160',
                   ('shell', 'getprop', 'ro.build.version.sdk'): '32',
                   ('shell', 'settings', 'get', 'system', 'font_scale'): '1.0'}
        def read(serial, *args):
            self.assertEqual(serial, 'private-test-target')
            self.calls.append(args)
            return answers[args]
        self.lab.adb_read = read
        self.lab.capture('private-test-target')
        saved = self.lab.profile_path.read_text(encoding='utf-8')
        self.assertNotIn('private-test-target', saved)
        self.assertEqual(set(json.loads(saved)), set(emulator.DEFAULT))
        self.assertEqual(len(self.calls), 5)


if __name__ == '__main__':
    unittest.main()
