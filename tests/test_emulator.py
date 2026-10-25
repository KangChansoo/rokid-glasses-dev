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

    def test_virtual_display_parser_rejects_missing_data(self):
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

    def test_physical_transport_is_rejected_before_any_command(self):
        self.lab.execute = lambda *args, **kw: self.fail('Must not send a command')
        for serial in ('physical-test', 'wireless-device-service', 'host:port'):
            with self.subTest(serial=serial), self.assertRaises(ValueError):
                self.lab.adb_read(serial, 'shell', 'getprop')

    def test_local_display_configuration_never_queries_a_physical_device(self):
        self.lab.target = lambda required=False: None
        self.lab._run = lambda *args, **kw: self.fail('No device query is needed')
        self.lab.configure_display(640, 480, 180, 1.15)
        profile = self.lab.profile()
        self.assertEqual((profile['width'], profile['height'], profile['density']), (640, 480, 180))
        self.assertEqual(profile['source'], 'manual')
        self.assertEqual(set(profile), set(emulator.DEFAULT))

    def test_display_change_is_rejected_while_the_virtual_machine_is_running(self):
        self.lab.target = lambda required=False: 'emulator-5586'
        with self.assertRaises(RuntimeError):
            self.lab.configure_display(640, 480, 180, 1.0)
        self.assertFalse(self.lab.profile_path.exists())

    def test_private_adb_disables_real_device_auto_connection(self):
        calls = []
        self.lab._run = lambda args, **kw: calls.append([str(arg) for arg in args]) or ''
        self.lab.execute([self.lab.adb, 'devices'])
        self.assertEqual(calls[0][1:], ['-P', str(emulator.ADB_PORT), '--one-device', emulator.NO_USB_DEVICE, 'start-server'])
        self.assertEqual(calls[1][1:], ['-P', str(emulator.ADB_PORT), 'devices'])
        self.assertEqual(self.lab.env['ADB_MDNS_AUTO_CONNECT'], '0')
        self.assertEqual(self.lab.env['ADB_SERVER_SOCKET'], f'tcp:127.0.0.1:{emulator.ADB_PORT}')
        self.assertEqual(self.lab.env['ANDROID_ADB_SERVER_PORT'], str(emulator.ADB_PORT))
        self.assertNotIn('ANDROID_SERIAL', self.lab.env)

    def test_connect_pair_and_physical_commands_are_unavailable(self):
        self.lab._run = lambda *args, **kw: self.fail('Must reject before starting any process')
        for command in (['connect', 'physical-test'], ['pair', 'physical-test'], ['disconnect'],
                        ['-s', 'physical-test', 'shell', 'getprop'],
                        ['-s', 'emulator-5586', 'connect', 'physical-test'],
                        ['-s', 'emulator-5586', 'pair', 'physical-test'],
                        ['-s', 'emulator-5586', 'tcpip', '5555']):
            with self.subTest(command=command), self.assertRaises(ValueError):
                self.lab.execute([self.lab.adb, *command])


class FilesAndNativeWindowIdentity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'toolchain.local.json').write_text(json.dumps({'sdkRoot': str(self.root / 'sdk')}), encoding='utf-8')
        self.lab = emulator.Lab(self.root)
        self.calls = []

    def test_generic_file_preserves_name_and_never_puts_it_in_shell(self):
        source = self.root / "한글 notes' test.txt"
        source.write_bytes(b'local test')
        self.lab.target = lambda: 'emulator-5554'
        def read(serial, *args):
            self.calls.append((serial, args))
            if args == ('shell', 'ls', '-1a', '/sdcard/Download'):
                return source.name + '\n'
            self.assertEqual(args, ('shell', 'mkdir', '-p', '/sdcard/Download'))
            return ''
        self.lab.adb_read = read
        def execute(args, **kwargs):
            self.calls.append(('push', [str(arg) for arg in args]))
            self.assertEqual(kwargs['timeout'], 600)
            return '1 file pushed'
        self.lab.execute = execute
        result = self.lab.send_file(source)
        self.assertIn("한글 notes' test (2).txt", result)
        self.assertEqual(self.calls[-1][1][-2:], [str(source), "/sdcard/Download/한글 notes' test (2).txt"])
        for serial, args in self.calls[:-1]:
            self.assertEqual(serial, 'emulator-5554')
            self.assertNotIn(source.name, args)

    def test_name_collisions_do_not_replace_existing_files(self):
        existing = {'sample.pdf', 'sample (2).pdf'}
        self.assertEqual(emulator.available_filename('sample.pdf', existing), 'sample (3).pdf')
        self.assertEqual(emulator.available_filename('README', {'README'}), 'README (2)')

    def test_missing_file_and_directory_are_rejected_before_target_lookup(self):
        self.lab.target = lambda: self.fail('Should not access a device')
        with self.assertRaises(FileNotFoundError):
            self.lab.send_file(self.root / 'missing.txt')
        with self.assertRaises(ValueError):
            self.lab.send_file(self.root)

    def test_invalid_remote_names_are_rejected(self):
        for name in ('../sample', 'a\\b', 'a\nb', 'a\rb', '', '.', '..', 'a' * 221):
            with self.subTest(name=name), self.assertRaises(ValueError):
                emulator.available_filename(name, set())

    def test_failed_push_is_reported_as_failure(self):
        source = self.root / 'sample.bin'; source.write_bytes(b'\x00\x01')
        self.lab.target = lambda: 'emulator-5554'
        self.lab.adb_read = lambda serial, *args: ''
        def fail(args, **kwargs):
            raise RuntimeError('Insufficient emulator storage')
        self.lab.execute = fail
        with self.assertRaisesRegex(RuntimeError, 'Insufficient'):
            self.lab.send_file(source)

    def test_native_host_requires_exact_avd_and_verified_port(self):
        title = 'Android Emulator - rokid_android32:5554'
        self.assertTrue(emulator.native_title_matches(title, 'emulator-5554'))
        self.assertFalse(emulator.native_title_matches(title, 'emulator-5556'))
        self.assertFalse(emulator.native_title_matches(title, 'physical-test'))
        self.assertFalse(emulator.native_title_matches('Editor - rokid_android32:5554'))
        self.assertFalse(emulator.native_title_matches('Android Emulator - other_avd:5554'))
        self.assertFalse(emulator.native_title_matches('Android Emulator - rokid_android32_extra:5554'))


if __name__ == '__main__':
    unittest.main()
